from logging import getLogger

from aiogram import F
from aiogram.fsm.context import FSMContext
from aiogram.types import CallbackQuery
from dishka.integrations.aiogram import FromDishka, inject

from src.application.services.conversation_manager import ConversationManager
from src.application.use_cases.analyze_logs_use_case import AnalyzeLogsUseCase
from src.application.use_cases.get_recent_errors_use_case import RecentErrorsUseCase
from src.application.use_cases.get_statistics_use_case import StatisticsLogsUseCase
from src.domain.entities.enums import ReportType
from src.domain.value_objects.time_range import TimeRange
from src.infrastructure.constants import MAX_ERRORS_IN_ONE_REPORT, TELEGRAM_MESSAGE_LIMIT, TextType
from src.infrastructure.dto import LLMSession
from src.infrastructure.settings.app_settings import AppSettings
from src.interfaces.bot.entities import BotAction, BotCallback, BotStates
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
    choose_an_action_msg,
    failed_msg,
    loading_msg,
    no_errors_msg,
)
from src.interfaces.bot.router import bot_router
from src.interfaces.bot.utils import (
    get_keyboard_from_state,
    send_or_edit_message_from_state,
)

logger = getLogger(__name__)


@bot_router.callback_query(F.data == BotCallback.ANALYZE.value)
async def on_llm_analysis(callback: CallbackQuery, state: FSMContext) -> None:
    await callback.answer()
    await send_or_edit_message_from_state(
        callback, state, choose_an_action_msg(), reply_markup=get_period_options(BotAction.ANALYZE)
    )

    await state.set_state(BotStates.period_selection)


@bot_router.callback_query(F.data == BotAction.RECENT.value)
async def on_recent_errors(callback: CallbackQuery, state: FSMContext) -> None:
    await callback.answer()
    await send_or_edit_message_from_state(
        callback, state, choose_an_action_msg(), reply_markup=get_period_options(BotAction.RECENT)
    )

    await state.set_state(BotStates.period_selection)


@bot_router.callback_query(F.data == BotCallback.STATS.value)
async def on_statistics_errors(callback: CallbackQuery, state: FSMContext) -> None:
    await callback.answer()
    await send_or_edit_message_from_state(
        callback, state, choose_an_action_msg(), reply_markup=get_period_options(BotAction.STATS)
    )

    await state.set_state(BotStates.period_selection)


@bot_router.callback_query(F.data == BotCallback.SETTINGS.value)
@inject
async def on_settings(
    callback: CallbackQuery, app_settings: FromDishka[AppSettings], state: FSMContext
) -> None:
    await callback.answer()
    info = BotTextFormatter.format_settings(app_settings)
    await state.set_state(BotStates.viewing_report)
    await callback.message.answer(
        info, reply_markup=get_main_menu(), parse_mode=TextType.HTML.value
    )


@bot_router.callback_query(F.data.startswith("analyze_"))
@inject
async def on_analyze_period(
    callback: CallbackQuery,
    analyze_use_case: FromDishka[AnalyzeLogsUseCase],
    helper: FromDishka[TelegramBotHelper],
    conv_manager: FromDishka[ConversationManager],
    state: FSMContext,
) -> None:
    await state.set_state(BotStates.viewing_report)

    chat_id = str(callback.message.chat.id)
    user_id = str(callback.from_user.id)
    time_range = helper.get_time_range_from_callback(callback)

    try:
        await callback.message.delete()
    except Exception:
        pass

    load_msg = await callback.message.answer(loading_msg(time_range))

    try:
        report = await analyze_use_case.execute(time_range, user_id)
        if not report.has_errors:
            keyboard = await get_keyboard_from_state(state)
            await load_msg.edit_text(no_errors_msg(time_range), reply_markup=keyboard)
            return

        if len(report.llm_analysis.analysis_text) > TELEGRAM_MESSAGE_LIMIT:
            await load_msg.delete()
            await helper.send_report(report, ReportType.ANALYZE, chat_id)
            menu_msg = await callback.message.answer(
                ask_llm_msg(), reply_markup=get_back_to_menu_button()
            )
            await state.update_data(menu_msg_id=menu_msg.message_id)
            await state.set_state(BotStates.waiting_for_question)
            return

        report_text = await helper.create_report(report, ReportType.ANALYZE)
        await load_msg.edit_text(report_text)
        menu_msg = await callback.message.answer(
            ask_llm_msg(), reply_markup=get_back_to_menu_button()
        )
        await state.update_data(menu_msg_id=menu_msg.message_id)
        await state.set_state(BotStates.waiting_for_question)

        session = LLMSession()
        if report.messages:
            session.add_bulk_messages(report.messages)
        session.add_message(role="assistant", content=report.llm_analysis.analysis_text)
        await conv_manager.save_session(chat_id, session)

    except Exception as e:
        logger.exception(e)
        await state.set_state(BotStates.error)
        await load_msg.edit_text(failed_msg(e, BotAction.ANALYZE), reply_markup=get_main_menu())


@bot_router.callback_query(F.data.startswith("recent_"))
@inject
async def on_recent_period(
    callback: CallbackQuery,
    errors_use_case: FromDishka[RecentErrorsUseCase],
    helper: FromDishka[TelegramBotHelper],
    state: FSMContext,
) -> None:
    await state.set_state(BotStates.viewing_report)
    time_range = helper.get_time_range_from_callback(callback)

    try:
        result = await errors_use_case.execute(time_range=time_range)
        if not result.has_errors:
            keyboard = await get_keyboard_from_state(state)
            await callback.message.edit_text(no_errors_msg(time_range), reply_markup=keyboard)
            return

        report = await helper.create_report(result, ReportType.RECENT)
        if len(result.logs) > MAX_ERRORS_IN_ONE_REPORT:  # type: ignore[arg-type]
            keyboard = get_more_errors_menu(len(result.logs))  # type: ignore[arg-type]
            await state.set_data(
                {
                    "hours": time_range.hours,
                    "report_msg_id": callback.message.message_id,
                }
            )
        else:
            keyboard = get_main_menu()

        await callback.message.edit_text(report, reply_markup=keyboard)
        await state.set_state(BotStates.viewing_report)

    except Exception as e:
        logger.exception(e)
        await state.set_state(BotStates.error)
        await callback.message.edit_text(
            failed_msg(e, BotAction.RECENT), reply_markup=get_main_menu()
        )


@bot_router.callback_query(F.data.startswith("stats_"))
@inject
async def on_statistics_period(
    callback: CallbackQuery,
    stats_use_case: FromDishka[StatisticsLogsUseCase],
    helper: FromDishka[TelegramBotHelper],
    state: FSMContext,
) -> None:
    await state.set_state(BotStates.viewing_report)
    time_range = helper.get_time_range_from_callback(callback)

    try:
        result = await stats_use_case.execute(time_range=time_range)
        if not result.has_errors:
            keyboard = await get_keyboard_from_state(state)
            await callback.message.edit_text(no_errors_msg(time_range), reply_markup=keyboard)
            return

        report = await helper.create_report(result, ReportType.STATS)
        await callback.message.edit_text(report, reply_markup=get_main_menu())
        await state.set_state(BotStates.viewing_report)

    except Exception as e:
        logger.exception(e)
        await state.set_state(BotStates.error)
        await callback.message.edit_text(
            failed_msg(e, BotAction.STATS), reply_markup=get_main_menu()
        )


@bot_router.callback_query(F.data == BotCallback.BACK_TO_MENU.value)
async def back_to_menu(callback: CallbackQuery, state: FSMContext) -> None:
    current_state = await state.get_state()

    await callback.answer()
    keyboard = await get_keyboard_from_state(state)
    await send_or_edit_message_from_state(callback, state, choose_an_action_msg(), keyboard)

    await state.set_data({})

    if current_state == BotStates.period_selection:
        await state.set_state(BotStates.back_to_main_menu)
    else:
        await state.set_state(BotStates.main_menu)


@bot_router.callback_query(F.data == BotCallback.YES_RECENT)
@inject
async def get_more_recent_errors(
    callback: CallbackQuery,
    errors_use_case: FromDishka[RecentErrorsUseCase],
    helper: FromDishka[TelegramBotHelper],
    state: FSMContext,
) -> None:
    data = await state.get_data()
    chat_id = str(callback.message.chat.id)
    time_range = TimeRange(data.get("hours"))  # type: ignore[arg-type]

    try:
        report = await errors_use_case.execute(time_range=time_range)

        if not report.has_errors:
            keyboard = await get_keyboard_from_state(state)
            await callback.message.edit_text(no_errors_msg(time_range), reply_markup=keyboard)
            return
        # падает 400
        await helper.send_report(report, ReportType.RECENT, chat_id, show_all_errors=True)
        await state.set_state(BotStates.viewing_report)

    except Exception as e:
        logger.exception(e)
        await state.set_state(BotStates.error)
        await callback.message.edit_text(
            failed_msg(e, BotAction.RECENT), reply_markup=get_main_menu()
        )
