from logging import getLogger

import msgspec
from aiogram import F
from aiogram.filters import Command, CommandStart, StateFilter
from aiogram.fsm.context import FSMContext
from aiogram.types import CallbackQuery, Message
from aiogram_dialog import DialogManager, StartMode
from dishka.integrations.aiogram import FromDishka, inject

from src.application.use_cases.analyze_logs_use_case import AnalyzeLogsUseCase
from src.application.use_cases.ask_llm_use_case import AskLLMUseCase
from src.application.use_cases.get_recent_errors_use_case import RecentErrorsUseCase
from src.application.use_cases.get_statistics_use_case import StatisticsLogsUseCase
from src.domain.entities.enums import ReportType
from src.domain.exceptions import LLMChatLimitExceededError
from src.domain.value_objects.time_range import TimeRange
from src.interfaces.bot.core.constants import EASTER_EGGS_WORT_LIST
from src.interfaces.bot.core.router import commands_router, fallback_router
from src.interfaces.bot.core.states import (
    AnalyzeSG,
    BugSG,
    HelpSG,
    MainSG,
    RecentSG,
    ScheduledSG,
    SettingsSG,
    StatsSG,
)
from src.interfaces.bot.formatters.html_formatter import ReportFormatter
from src.interfaces.bot.utils.messages import (
    ask_llm_more_questions_msg,
    error_msg,
    invalid_hour_range_msg,
    llm_limit_chat_msg,
    no_errors_msg,
    operation_failed_msg,
    unknown_command_in_menu_msg,
    unknown_command_msg,
)

logger = getLogger(__name__)


@commands_router.message(CommandStart())
async def cmd_start(message: Message, dialog_manager: DialogManager) -> None:
    await dialog_manager.start(MainSG.menu, mode=StartMode.RESET_STACK)


@commands_router.message(Command("analyze"))
@inject
async def cmd_analyze(
    message: Message,
    dialog_manager: DialogManager,
    analyze_use_case: FromDishka[AnalyzeLogsUseCase],
) -> None:
    user_id = message.from_user.id
    try:
        period = message.text.split(" ")[-1]

        if not period.isdigit():
            await dialog_manager.start(AnalyzeSG.period_selection, mode=StartMode.RESET_STACK)
            return

        time_range = TimeRange(int(period))
        report = await analyze_use_case.execute(time_range, int(user_id))  # type:ignore[arg-type]

        if not report.has_errors:
            await message.answer(no_errors_msg(time_range))
            return

        await dialog_manager.start(
            AnalyzeSG.viewing_data,
            mode=StartMode.RESET_STACK,
            data={"report": msgspec.to_builtins(report)},
        )

    except ValueError:
        await message.answer(invalid_hour_range_msg())
    except Exception as e:
        logger.exception(f"Failed to get stats: {e}")
        await message.answer(error_msg())


@commands_router.message(Command("recent"))
@inject
async def cmd_recent(
    message: Message,
    dialog_manager: DialogManager,
    recent_use_case: FromDishka[RecentErrorsUseCase],
) -> None:
    try:
        period = message.text.split(" ")[-1]

        if not period.isdigit():
            await dialog_manager.start(RecentSG.period_selection, mode=StartMode.RESET_STACK)
            return

        time_range = TimeRange(int(period))
        report = await recent_use_case.execute(time_range)

        if not report.has_errors:
            await message.answer(no_errors_msg(time_range))
            return

        await dialog_manager.start(
            RecentSG.viewing_data,
            mode=StartMode.RESET_STACK,
            data={"report": msgspec.to_builtins(report)},
        )

    except ValueError:
        await message.answer(invalid_hour_range_msg())
    except Exception as e:
        logger.exception(f"Failed to get stats: {e}")
        await message.answer(error_msg())


@commands_router.message(Command("stats"))
@inject
async def cmd_stats(
    message: Message,
    dialog_manager: DialogManager,
    stats_use_case: FromDishka[StatisticsLogsUseCase],
) -> None:
    try:
        period = message.text.split(" ")[-1]

        if not period.isdigit():
            await dialog_manager.start(StatsSG.period_selection, mode=StartMode.RESET_STACK)
            return

        time_range = TimeRange(int(period))
        report = await stats_use_case.execute(time_range)

        if not report.has_errors:
            await message.answer(no_errors_msg(time_range))
            return

        await dialog_manager.start(
            StatsSG.viewing_data,
            mode=StartMode.RESET_STACK,
            data={"report": msgspec.to_builtins(report)},
        )

    except ValueError:
        await message.answer(invalid_hour_range_msg())
    except Exception as e:
        logger.exception(f"Failed to get stats: {e}")
        await message.answer(error_msg())


@commands_router.message(Command("settings"))
async def cmd_settings(message: Message, dialog_manager: DialogManager) -> None:
    await dialog_manager.start(SettingsSG.viewing_data, mode=StartMode.RESET_STACK)


@commands_router.message(Command("bug"))
async def cmd_bug(message: Message, dialog_manager: DialogManager) -> None:
    await dialog_manager.start(BugSG.reporting, mode=StartMode.RESET_STACK)


@commands_router.message(Command("help"))
async def cmd_help(message: Message, dialog_manager: DialogManager) -> None:
    await dialog_manager.start(HelpSG.viewing_data, mode=StartMode.RESET_STACK)


@commands_router.message(Command("menu"))
async def cmd_menu(message: Message, dialog_manager: DialogManager) -> None:
    await dialog_manager.start(MainSG.menu, mode=StartMode.RESET_STACK)


@fallback_router.message()
async def handle_unknown_message(
    message: Message, dialog_manager: DialogManager, state: FSMContext
) -> None:
    current_state = await state.get_state()

    if message.text in EASTER_EGGS_WORT_LIST:
        match message.text:
            case "ogonek":
                await message.answer("https://ogonek.app")
            case "author":
                await message.answer("https://github.com/SokolovG")
        return

    if current_state is None:
        await message.answer(unknown_command_msg())
        await dialog_manager.start(MainSG.menu, mode=StartMode.RESET_STACK)


@commands_router.callback_query(F.data == "main_menu")
async def on_scheduled_menu(
    callback: CallbackQuery, dialog_manager: DialogManager, state: FSMContext
) -> None:
    await callback.answer()
    await state.clear()
    await dialog_manager.start(MainSG.menu, mode=StartMode.RESET_STACK)


@commands_router.message(StateFilter(ScheduledSG.asking_questions))
@inject
async def on_scheduled_llm_question(
    message: Message,
    state: FSMContext,
    ask_use_case: FromDishka[AskLLMUseCase],
    formatter: FromDishka[ReportFormatter],
) -> None:
    try:
        question: str = message.text  # type: ignore
        user_id = str(message.from_user.id)

        answer = await ask_use_case.execute(question, user_id)
        html = formatter.format_llm_answer(answer, ReportType.ANSWER)
        await message.answer(f"{html}\n\n{ask_llm_more_questions_msg()}")

    except LLMChatLimitExceededError as e:
        limit = e.details.get("limit")
        await message.answer(llm_limit_chat_msg(limit))
        await state.clear()

    except Exception as e:
        logger.exception(operation_failed_msg(e))
        await message.answer(error_msg())
        await state.clear()
