from logging import getLogger

from aiogram.filters import Command, CommandStart
from aiogram.fsm.context import FSMContext
from aiogram.types import Message
from dishka.integrations.aiogram import FromDishka, inject

from src.application.use_cases.analyze_logs_use_case import AnalyzeLogsUseCase
from src.application.use_cases.ask_llm_use_case import AskLLMUseCase
from src.application.use_cases.get_recent_errors_use_case import RecentErrorsUseCase
from src.application.use_cases.get_statistics_use_case import StatisticsLogsUseCase
from src.domain.entities.enums import ReportType
from src.domain.utils import format_time_range
from src.domain.value_objects.time_range import TimeRange
from src.infrastructure.constants import MAX_ERRORS_IN_ONE_REPORT
from src.infrastructure.enums import TextType
from src.infrastructure.settings.app_settings import AppSettings
from src.interfaces.bot import callbacks  # noqa: ignore
from src.interfaces.bot.entities import BotAction, BotStates
from src.interfaces.bot.formatters.text_formatter import BotTextFormatter
from src.interfaces.bot.helpers import TelegramBotHelper
from src.interfaces.bot.keyboards import (
    get_back_to_menu_button,
    get_main_menu,
    get_more_errors_menu,
    get_period_options,
)
from src.interfaces.bot.messages import (
    ask_llm_msg,
    asking_llm_message,
    choose_an_action_msg,
    choose_period_msg,
    failed_msg,
    greetings_msg,
    loading_msg,
    no_errors_msg,
)
from src.interfaces.bot.router import bot_router

logger = getLogger(__name__)


@bot_router.message(CommandStart())
async def cmd_start(message: Message) -> None:
    await message.answer(
        text=greetings_msg(),
        reply_markup=get_main_menu(),
    )


@bot_router.message(Command(BotAction.ANALYZE.value))
@inject
async def cmd_analyze(
    message: Message,
    use_case: FromDishka[AnalyzeLogsUseCase],
    helper: FromDishka[TelegramBotHelper],
) -> None:
    chat_id = str(message.chat.id)
    args = message.text.split()[1:] if message.text else []
    if not args:
        await message.answer(
            text=choose_period_msg(), reply_markup=get_period_options(BotAction.ANALYZE)
        )
        return

    time_range = TimeRange(int(args[0]))
    load_msg = await message.answer(loading_msg(time_range))

    try:
        report = await use_case.execute(time_range=time_range)
        if not report.has_errors:
            await load_msg.edit_text(no_errors_msg(time_range), reply_markup=get_main_menu())
            return

        await load_msg.delete()
        await helper.send_report(report, ReportType.ANALYZE, chat_id)
        await helper.send_menu(chat_id, ask_llm_msg(), get_back_to_menu_button())

    except Exception as e:
        logger.exception(e)
        await load_msg.edit_text(failed_msg(e, BotAction.ANALYZE), reply_markup=get_main_menu())


@bot_router.message(Command(BotAction.STATS.value))
@inject
async def cmd_stats(
    message: Message,
    use_case: FromDishka[StatisticsLogsUseCase],
    helper: FromDishka[TelegramBotHelper],
    state: FSMContext,
) -> None:
    chat_id = str(message.chat.id)
    args = helper.parse_args_from_text(message.text)

    if not args:
        await message.answer(choose_period_msg(), reply_markup=get_period_options(BotAction.STATS))
        return

    try:
        time_range = TimeRange(int(args[0]))
        report = await use_case.execute(time_range=time_range)
        if not report.has_errors:
            await message.edit_text(no_errors_msg(time_range), reply_markup=get_main_menu())
            return

        await helper.send_report(report, ReportType.STATS, chat_id)
        await helper.send_menu(chat_id, choose_an_action_msg(), get_main_menu())
        await state.set_state(BotStates.viewing_report)

    except Exception as e:
        logger.exception(e)
        await message.edit_text(failed_msg(e, BotAction.STATS), reply_markup=get_main_menu())


@bot_router.message(Command(BotAction.RECENT.value))
@inject
async def cmd_recent(
    message: Message,
    use_case: FromDishka[RecentErrorsUseCase],
    helper: FromDishka[TelegramBotHelper],
    state: FSMContext,
) -> None:
    chat_id = str(message.chat.id)
    args = helper.parse_args_from_text(message.text)

    if not args:
        await message.answer(choose_period_msg(), reply_markup=get_period_options(BotAction.STATS))
        return

    try:
        time_range = TimeRange(int(args[0]))
        report = await use_case.execute(time_range=time_range)

        if not report.has_errors:
            await message.edit_text(no_errors_msg(time_range), reply_markup=get_main_menu())
            return

        report_msg = await helper.send_report(report, ReportType.RECENT, chat_id)
        if len(report.logs) > MAX_ERRORS_IN_ONE_REPORT:  # type: ignore[arg-type]
            keyboard = get_more_errors_menu(len(report.logs))  # type: ignore[arg-type]
            await state.set_data(
                {
                    "hours": time_range.hours,
                    "report_msg_id": report_msg.message_id,
                }
            )
        else:
            keyboard = get_main_menu()

        menu_msg = await helper.send_menu(chat_id, choose_an_action_msg(), keyboard)
        # TODO: Сохранить [report_msg, menu_msg] для удаления
        await state.set_state(BotStates.waiting_for_question)

    except Exception as e:
        logger.exception(e)
        await message.edit_text(failed_msg(e, BotAction.RECENT), reply_markup=get_main_menu())


@bot_router.message(Command(BotAction.SETTINGS.value))
@inject
async def cmd_settings(message: Message, app_settings: FromDishka[AppSettings]) -> None:
    info = BotTextFormatter.format_settings(
        provider=app_settings.llm_provider.provider,
        model=app_settings.llm.model,
        schedule_hourse=TimeRange(int(app_settings.schedule_interval_hours)),
        schedule_enabled=app_settings.schedule_enabled,
    )
    await message.answer(info, parse_mode=TextType.HTML.value)


@bot_router.message(Command(BotAction.HELP.value))
async def cmd_help(message: Message) -> None:
    help_text = BotTextFormatter.format_help()
    await message.answer(help_text, parse_mode=TextType.HTML.value, reply_markup=get_main_menu())


@bot_router.message(BotStates.waiting_for_question)
@inject
async def handle_llm_question(
    message: Message,
    ask_use_case: FromDishka[AskLLMUseCase],
    helper: FromDishka[TelegramBotHelper],
    state: FSMContext,
) -> None:
    question = message.text
    chat_id = str(message.chat.id)

    loading_msg = await message.answer(text=asking_llm_message())
    session_id = str(message.chat.id)

    try:
        answer = await ask_use_case.execute(question, session_id)
        await helper.send_llm_answer(answer, chat_id)
        await loading_msg.delete()
        await helper.send_menu(chat_id, choose_an_action_msg(), get_main_menu())
        await state.set_state(BotStates.main_menu)

    except Exception as e:
        logger.exception(e)
        await message.edit_text(failed_msg(e, BotAction.ASK), reply_markup=get_main_menu())


@bot_router.message()
async def easter_egg(message: Message) -> None:
    if message.text == "ogonek":
        await message.answer("https://ogonek.app")
