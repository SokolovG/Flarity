from logging import getLogger

from aiogram.filters import Command, CommandStart
from aiogram.fsm.context import FSMContext
from aiogram.types import Message
from dishka.integrations.aiogram import FromDishka, inject

from src.application.dto.analysis_result import LLMAnalysisResult
from src.application.use_cases.analyze_logs_use_case import AnalyzeLogsUseCase
from src.application.use_cases.ask_llm_use_case import AskLLMUseCase
from src.application.use_cases.get_recent_errors_use_case import RecentErrorsUseCase
from src.application.use_cases.get_statistics_use_case import StatisticsLogsUseCase
from src.domain.entities.enums import ReportType
from src.infrastructure.constants import MAX_ERRORS_IN_ONE_REPORT, TextType
from src.infrastructure.exceptions.base_exceptions import InfrastructureException
from src.infrastructure.settings.app_settings import AppSettings
from src.interfaces.bot import callbacks  # noqa: F401
from src.interfaces.bot.constants import EASTER_EGGS_WORT_LIST, MAX_LLM_MESSAGES_IN_ONE_CHAT
from src.interfaces.bot.entities import BotAction, BotStates
from src.interfaces.bot.formatters.text_formatter import BotTextFormatter
from src.interfaces.bot.helpers import TelegramBotHelper
from src.interfaces.bot.keyboards import (
    get_back_to_menu_button,
    get_main_menu,
    get_more_errors_menu,
)
from src.interfaces.bot.messages import (
    ask_llm_one_more_time_msg,
    asking_llm_message,
    choose_an_action_msg,
    failed_msg,
    greetings_msg,
    llm_limit_msg,
    loading_msg,
    no_errors_msg,
)
from src.interfaces.bot.router import bot_router

logger = getLogger(__name__)


@bot_router.message(CommandStart())
async def cmd_start(message: Message, state: FSMContext) -> None:
    await state.set_state(BotStates.start)
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
    state: FSMContext,
) -> None:
    chat_id = str(message.chat.id)
    user_id = str(message.from_user.id)

    time_range = await helper.get_time_range_from_msg(message, BotAction.ANALYZE, state)
    if not time_range:
        return
    load_msg = await message.answer(loading_msg(time_range))

    try:
        report = await use_case.execute(time_range, user_id)
        if not report.has_errors:
            await load_msg.edit_text(no_errors_msg(time_range), reply_markup=get_main_menu())
            return

        await load_msg.delete()
        await helper.send_report(
            report, ReportType.ANALYZE, chat_id, reply_markup=get_back_to_menu_button()
        )
        await state.set_state(BotStates.waiting_for_question)

    except Exception as e:
        if not isinstance(e, InfrastructureException):
            logger.exception(e)
        else:
            logger.error(e)
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
    time_range = await helper.get_time_range_from_msg(message, BotAction.STATS, state)
    if not time_range:
        return

    try:
        report = await use_case.execute(time_range=time_range)
        if not report.has_errors:
            await message.answer(no_errors_msg(time_range), reply_markup=get_main_menu())
            return

        await helper.send_report(report, ReportType.STATS, chat_id, reply_markup=get_main_menu())
        await state.set_state(BotStates.viewing_data)

    except Exception as e:
        if not isinstance(e, InfrastructureException):
            logger.exception(e)
        else:
            logger.error(e)
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
    time_range = await helper.get_time_range_from_msg(message, BotAction.RECENT, state)
    if not time_range:
        return

    try:
        report = await use_case.execute(time_range=time_range)

        if not report.has_errors:
            await message.answer(no_errors_msg(time_range), reply_markup=get_main_menu())
            return

        if len(report.logs) > MAX_ERRORS_IN_ONE_REPORT:  # type:ignore[arg-type]
            keyboard = get_more_errors_menu(len(report.logs))  # type:ignore[arg-type]
        else:
            keyboard = get_main_menu()

        await helper.send_report(report, ReportType.RECENT, chat_id, reply_markup=keyboard)
        if len(report.logs) > MAX_ERRORS_IN_ONE_REPORT:  # type:ignore[arg-type]
            await state.update_data(hours=time_range.hours)
        await state.set_state(BotStates.waiting_for_question)

    except Exception as e:
        if not isinstance(e, InfrastructureException):
            logger.exception(e)
        else:
            logger.error(e)
        await message.edit_text(failed_msg(e, BotAction.RECENT), reply_markup=get_main_menu())


@bot_router.message(Command(BotAction.SETTINGS.value))
@inject
async def cmd_settings(
    message: Message, app_settings: FromDishka[AppSettings], state: FSMContext
) -> None:
    info = BotTextFormatter.format_settings(app_settings)
    await state.set_state(BotStates.viewing_data)
    await message.answer(info, reply_markup=get_main_menu(), parse_mode=TextType.HTML.value)


@bot_router.message(Command(BotAction.HELP.value))
async def cmd_help(message: Message, state: FSMContext) -> None:
    await state.set_state(BotStates.viewing_data)
    help_text = BotTextFormatter.format_help()
    await message.answer(help_text, parse_mode=TextType.HTML.value, reply_markup=get_main_menu())


@bot_router.message(Command(BotAction.MENU.value))
async def cmd_menu(message: Message, state: FSMContext) -> None:
    await state.set_state(BotStates.main_menu)
    await message.answer(
        text=choose_an_action_msg(), parse_mode=TextType.HTML.value, reply_markup=get_main_menu()
    )


@bot_router.message(BotStates.waiting_for_question)
@inject
async def handle_llm_question(
    message: Message,
    ask_use_case: FromDishka[AskLLMUseCase],
    helper: FromDishka[TelegramBotHelper],
    state: FSMContext,
) -> None:
    data = await state.get_data()
    report_msg_id = data.get("report_msg_id")

    if report_msg_id:
        try:
            await message.bot.edit_message_reply_markup(
                chat_id=message.chat.id, message_id=report_msg_id, reply_markup=None
            )
        except Exception:
            pass

    question_count = data.get("question_count", 0)

    if question_count >= MAX_LLM_MESSAGES_IN_ONE_CHAT:
        await message.answer(
            text=llm_limit_msg(MAX_LLM_MESSAGES_IN_ONE_CHAT), reply_markup=get_main_menu()
        )
        await state.set_state(BotStates.main_menu)
        await state.set_data({})
        return

    if message.text in ["/menu"]:
        await message.answer(choose_an_action_msg(), reply_markup=get_main_menu())
        await state.set_state(BotStates.main_menu)
        return

    question = message.text
    if not question:
        return

    chat_id = str(message.chat.id)
    user_id = str(message.from_user.id)

    loading_msg = await message.answer(text=asking_llm_message())

    try:
        answer: LLMAnalysisResult = await ask_use_case.execute(question, user_id)

        await helper.send_llm_answer(answer, chat_id)
        await loading_msg.delete()

        await helper.send_menu(chat_id, ask_llm_one_more_time_msg(), get_back_to_menu_button())
        await state.update_data(question_count=question_count + 1)

    except Exception as e:
        if not isinstance(e, InfrastructureException):
            logger.exception(e)
        else:
            logger.error(e)
        await loading_msg.delete()
        await message.answer(failed_msg(e, BotAction.ASK), reply_markup=get_main_menu())


@bot_router.message()
async def easter_egg_or_handle_wrong_msg(message: Message, state: FSMContext) -> None:
    if message.text in EASTER_EGGS_WORT_LIST:
        await state.set_state(BotStates.viewing_data)
        match message.text:
            case "ogonek":
                await message.answer("https://ogonek.app")
            case "author":
                await message.answer("https://github.com/SokolovG")
    else:
        await message.answer("I don't understand you! Please use /help.")


@bot_router.message()
async def notify_about_bug(message: Message) -> None:
    if message.text.startswith("bug"):
        # TODO: notify me
        ...
