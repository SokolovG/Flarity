from logging import getLogger

from aiogram import F
from aiogram.fsm.context import FSMContext
from aiogram.types import CallbackQuery
from dishka.integrations.aiogram import FromDishka, inject

from src.application.ports.notifier import Notifier
from src.application.use_cases.analyze_logs_use_case import AnalyzeLogsUseCase
from src.application.use_cases.get_recent_errors_use_case import RecentErrorsUseCase
from src.application.use_cases.get_statistics_use_case import StatisticsLogsUseCase
from src.domain.entities.enums import ReportType
from src.domain.utils import format_time_range
from src.domain.value_objects.time_range import TimeRange
from src.infrastructure.constants import MAX_ERRORS_IN_ONE_REPORT
from src.infrastructure.entities import LLMSession
from src.infrastructure.enums import TextType
from src.infrastructure.settings.app_settings import AppSettings
from src.interfaces.bot.entities import BotAction, BotCallback, BotStates
from src.interfaces.bot.formatters.html_formatter import ReportFormatter
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
    choose_period_msg,
    failed_msg,
    loading_msg,
    no_errors_msg,
)
from src.interfaces.bot.router import bot_router

logger = getLogger(__name__)


@bot_router.callback_query(F.data == BotCallback.ANALYZE.value)
async def on_llm_analysis(callback: CallbackQuery, state: FSMContext) -> None:
    if not callback.message:
        return

    await callback.answer()
    await state.set_state(BotStates.period_selection)
    await callback.message.answer(
        text=choose_period_msg(), reply_markup=get_period_options(BotAction.ANALYZE)
    )


@bot_router.callback_query(F.data == BotAction.RECENT.value)
async def on_recent_errors(callback: CallbackQuery, state: FSMContext) -> None:
    if not callback.message:
        return

    await callback.answer()
    await state.set_state(BotStates.period_selection)
    await callback.message.answer(
        text=choose_period_msg(), reply_markup=get_period_options(BotAction.RECENT)
    )


@bot_router.callback_query(F.data == BotCallback.STATS.value)
async def on_statistics_errors(callback: CallbackQuery, state: FSMContext) -> None:
    if not callback.message:
        return

    await state.set_state(BotStates.period_selection)
    await callback.message.answer(
        text=choose_period_msg(), reply_markup=get_period_options(BotAction.STATS)
    )


@bot_router.callback_query(F.data == BotCallback.SETTINGS.value)
@inject
async def on_settings(
    callback: CallbackQuery, app_settings: FromDishka[AppSettings], state: FSMContext
) -> None:
    if not callback.message:
        return

    await callback.answer()
    info = BotTextFormatter.format_settings(
        provider=app_settings.llm_provider.provider,
        model=app_settings.llm.model,
        schedule_hourse=TimeRange(int(app_settings.schedule_interval_hours)),
        schedule_enabled=app_settings.schedule_enabled,
    )
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
    state: FSMContext,
) -> None:
    if not callback.message:
        return

    await state.set_state(BotStates.viewing_report)

    chat_id = str(callback.message.chat.id)
    time_range = helper.get_time_range_from_callback(callback)

    load_msg = await callback.message.edit_text(loading_msg(time_range))

    try:
        report = await analyze_use_case.execute(time_range)
        if not report.has_errors:
            await load_msg.edit_text(no_errors_msg(time_range), reply_markup=get_main_menu())
            return

        await load_msg.delete()

        await helper.send_report(report, ReportType.ANALYZE, chat_id)
        await helper.send_menu(chat_id, ask_llm_msg(), get_back_to_menu_button())
        await state.set_state(BotStates.waiting_for_question)

        session = LLMSession()
        session.add_bulk_messages(report.messages)
        session.add_message(role="assistant", content=report.llm_analysis.analysis_text)

    except Exception as e:
        logger.exception(e)
        await load_msg.edit_text(failed_msg(e, BotAction.ANALYZE), reply_markup=get_main_menu())


@bot_router.callback_query(F.data.startswith("recent_"))
@inject
async def on_recent_period(
    callback: CallbackQuery,
    errors_use_case: FromDishka[RecentErrorsUseCase],
    helper: FromDishka[TelegramBotHelper],
    state: FSMContext,
) -> None:
    if not callback.message:
        return

    await state.set_state(BotStates.viewing_report)

    time_range = helper.get_time_range_from_callback(callback)
    chat_id = str(callback.message.chat.id)

    try:
        report = await errors_use_case.execute(time_range=time_range)
        if not report.has_errors:
            await callback.message.edit_text(
                no_errors_msg(time_range), reply_markup=get_main_menu()
            )
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

        await state.set_state(BotStates.main_menu)

    except Exception as e:
        logger.exception(e)
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
    if not callback.message:
        return

    await state.set_state(BotStates.viewing_report)
    time_range = helper.get_time_range_from_callback(callback)
    chat_id = str(callback.message.chat.id)

    try:
        report = await stats_use_case.execute(time_range=time_range)
        if not report.has_errors:
            await callback.message.edit_text(
                no_errors_msg(time_range), reply_markup=get_main_menu()
            )
            return

        await helper.send_report(report, ReportType.STATS, chat_id)
        await helper.send_menu(chat_id, choose_an_action_msg(), get_main_menu())
        await state.set_state(BotStates.main_menu)

    except Exception as e:
        logger.exception(e)
        await callback.message.edit_text(
            failed_msg(e, BotAction.STATS), reply_markup=get_main_menu()
        )


@bot_router.callback_query(F.data == BotCallback.BACK_TO_MENU.value)
@bot_router.callback_query(F.data == BotCallback.NO.value)
async def back_to_menu(callback: CallbackQuery, state: FSMContext) -> None:
    if not callback.message:
        return

    await callback.answer()
    current_state = await state.get_state()
    if current_state == BotStates.viewing_report or current_state == BotStates.waiting_for_question:
        await callback.message.answer(text=choose_an_action_msg(), reply_markup=get_main_menu())
    else:
        await callback.message.edit_text(text=choose_an_action_msg(), reply_markup=get_main_menu())

    await state.set_state(BotStates.main_menu)


@bot_router.callback_query(F.data == BotCallback.YES_RECENT)
@inject
async def get_more_recent_errors(
    callback: CallbackQuery,
    errors_use_case: FromDishka[RecentErrorsUseCase],
    helper: FromDishka[TelegramBotHelper],
    state: FSMContext,
) -> None:
    if not callback.message:
        return

    data = await state.get_data()
    chat_id = str(callback.message.chat.id)
    time_range = TimeRange(data.get("hours"))  # type: ignore[arg-type]

    try:
        report = await errors_use_case.execute(time_range=time_range)

        if not report.has_errors:
            await callback.message.edit_text(
                no_errors_msg(time_range), reply_markup=get_main_menu()
            )
            return

        await helper.send_report(report, ReportType.RECENT, chat_id, show_all_errors=True)
        await helper.send_menu(chat_id, choose_an_action_msg(), get_main_menu())
        await state.set_state(BotStates.viewing_report)

    except Exception as e:
        logger.exception(e)
        await callback.message.edit_text(
            failed_msg(e, BotAction.RECENT), reply_markup=get_main_menu()
        )
