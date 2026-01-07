from logging import getLogger

from aiogram.filters import Command, CommandStart
from aiogram.fsm.context import FSMContext
from aiogram.types import Message
from dishka.integrations.aiogram import FromDishka, inject

from src.application.dto.analysis_result import LLMAnalysisResult
from src.application.services.conversation_manager import ConversationManager
from src.application.use_cases.analyze_logs_use_case import AnalyzeLogsUseCase
from src.application.use_cases.ask_llm_use_case import AskLLMUseCase
from src.application.use_cases.get_recent_errors_use_case import RecentErrorsUseCase
from src.application.use_cases.get_statistics_use_case import StatisticsLogsUseCase
from src.domain.entities.enums import ReportType
from src.infrastructure.constants import MAX_ERRORS_IN_ONE_REPORT, TextType
from src.infrastructure.settings.app_settings import AppSettings
from src.interfaces.bot import callbacks  # noqa: F401
from src.interfaces.bot.constants import MAX_LLM_MESSAGES_IN_ONE_CHAT
from src.interfaces.bot.entities import BotAction, BotStates
from src.interfaces.bot.formatters.text_formatter import BotTextFormatter
from src.interfaces.bot.helpers import TelegramBotHelper
from src.interfaces.bot.keyboards import (
    get_back_to_menu_button,
    get_main_menu,
    get_more_errors_menu,
)
from src.interfaces.bot.messages import (
    ask_llm_msg,
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
        await helper.send_report(report, ReportType.ANALYZE, chat_id)
        await helper.send_menu(chat_id, ask_llm_msg(), get_back_to_menu_button())

    except Exception as e:
        logger.exception(e)
        await state.set_state(BotStates.error)
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

        report_msg = await helper.send_report(report, ReportType.STATS, chat_id)
        menu_msg = await helper.send_menu(chat_id, choose_an_action_msg(), get_main_menu())

        await state.update_data(
            menu_msg_id=menu_msg.message_id,
            last_report_msg_id=report_msg.message_id,
        )
        await state.set_state(BotStates.viewing_report)

    except Exception as e:
        logger.exception(e)
        await state.set_state(BotStates.error)
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

        report_msg = await helper.send_report(report, ReportType.RECENT, chat_id)
        if len(report.logs) > MAX_ERRORS_IN_ONE_REPORT:  # type: ignore[arg-type]
            keyboard = get_more_errors_menu(len(report.logs))  # type: ignore[arg-type]
            await state.update_data(
                hours=time_range.hours,
                report_msg_id=report_msg.message_id,
            )
        else:
            keyboard = get_main_menu()

        menu_msg = await helper.send_menu(chat_id, choose_an_action_msg(), keyboard)
        await state.update_data(
            menu_msg_id=menu_msg.message_id,
            last_report_msg_id=report_msg.message_id,
        )
        await state.set_state(BotStates.waiting_for_question)

    except Exception as e:
        logger.exception(e)
        await state.set_state(BotStates.error)
        await message.edit_text(failed_msg(e, BotAction.RECENT), reply_markup=get_main_menu())


@bot_router.message(Command(BotAction.SETTINGS.value))
@inject
async def cmd_settings(message: Message, app_settings: FromDishka[AppSettings]) -> None:
    info = BotTextFormatter.format_settings(app_settings)
    await message.answer(info, parse_mode=TextType.HTML.value)


@bot_router.message(Command(BotAction.HELP.value))
async def cmd_help(message: Message) -> None:
    help_text = BotTextFormatter.format_help()
    await message.answer(help_text, parse_mode=TextType.HTML.value, reply_markup=get_main_menu())


@bot_router.message(Command(BotAction.MENU.value))
async def cmd_menu(message: Message) -> None:
    await message.answer(
        text=choose_an_action_msg(), parse_mode=TextType.HTML.value, reply_markup=get_main_menu()
    )


@bot_router.message(BotStates.waiting_for_question)
@inject
async def handle_llm_question(
    message: Message,
    ask_use_case: FromDishka[AskLLMUseCase],
    helper: FromDishka[TelegramBotHelper],
    conv_manager: FromDishka[ConversationManager],
    state: FSMContext,
) -> None:
    data = await state.get_data()
    old_menu_msg_id = data.get("menu_msg_id")
    question_count = data.get("question_count", 0)

    if old_menu_msg_id:
        try:
            await message.bot.delete_message(message.chat.id, old_menu_msg_id)
        except Exception:
            pass

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
        session = await conv_manager.get_session(chat_id)
        if session:
            session.add_message("user", question)
            session.add_message(role="assistant", text=answer.analysis_text)
            await conv_manager.save_session(chat_id, session)

        await helper.send_llm_answer(answer, chat_id)
        await loading_msg.delete()

        menu_msg = await helper.send_menu(
            chat_id, ask_llm_one_more_time_msg(), get_back_to_menu_button()
        )
        await state.update_data(menu_msg_id=menu_msg.message_id)
        await state.update_data(question_count=question_count + 1)

    except Exception as e:
        logger.exception(e)
        await state.set_state(BotStates.error)
        await loading_msg.delete()
        error_menu_msg = await message.answer(
            failed_msg(e, BotAction.ASK), reply_markup=get_main_menu()
        )
        await state.update_data(menu_msg_id=error_menu_msg.message_id)


@bot_router.message()
async def easter_egg(message: Message) -> None:
    if message.text == "ogonek":
        await message.answer("https://ogonek.app")
