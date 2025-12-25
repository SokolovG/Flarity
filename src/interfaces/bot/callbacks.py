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
from src.infrastructure.settings.app_settings import AppSettings
from src.interfaces.bot.entities import BotAction, BotCallback, BotStates
from src.interfaces.bot.formatters.html_formatter import ReportFormatter
from src.interfaces.bot.formatters.text_formatter import BotTextFormatter
from src.interfaces.bot.helpers import handle_report_callback
from src.interfaces.bot.keyboards import get_main_menu, get_period_options
from src.interfaces.bot.router import bot_router

logger = getLogger(__name__)


@bot_router.callback_query(F.data == BotCallback.ANALYZE.value)
async def on_llm_analysis(callback: CallbackQuery, state: FSMContext) -> None:
    await callback.answer()
    await state.set_state(BotStates.period_selection)
    await callback.message.edit_text(
        "Choose analysis period:", reply_markup=get_period_options(BotAction.ANALYZE)
    )


@bot_router.callback_query(F.data == BotAction.RECENT.value)
async def on_recent_errors(callback: CallbackQuery, state: FSMContext) -> None:
    await callback.answer()
    await state.set_state(BotStates.period_selection)
    await callback.message.edit_text(
        "Choose period:", reply_markup=get_period_options(BotAction.RECENT)
    )


@bot_router.callback_query(F.data == BotCallback.STATS.value)
async def on_statistics_errors(callback: CallbackQuery, state: FSMContext) -> None:
    await state.set_state(BotStates.period_selection)
    await callback.message.edit_text(
        "Choose period:", reply_markup=get_period_options(BotAction.STATS)
    )


@bot_router.callback_query(F.data == BotCallback.SETTINGS.value)
@inject
async def on_settings(callback: CallbackQuery, app_settings: FromDishka[AppSettings]) -> None:
    await callback.answer()
    info = BotTextFormatter.format_settings(
        provider=app_settings.llm_provider.provider,
        model=app_settings.llm.model,
        schedule_hourse=TimeRange(int(app_settings.schedule_interval_hours)),
        schedule_enabled=app_settings.schedule_enabled,
    )
    await callback.message.answer(info, reply_markup=get_main_menu(), parse_mode="HTML")


@bot_router.callback_query(F.data.startswith("analyze_"))
@inject
async def on_analyze_period(
    callback: CallbackQuery,
    analyze_use_case: FromDishka[AnalyzeLogsUseCase],
    formatter: FromDishka[ReportFormatter],
    notifier: FromDishka[Notifier],
    state: FSMContext,
) -> None:
    await state.set_state(BotStates.viewing_report)

    hours = int(callback.data.split("_")[1])
    time_range = TimeRange(hours)

    loading_msg = await callback.message.edit_text(
        f"Analyze logs for last {hours} {format_time_range(time_range)}\n"
        "This may take up to 30 seconds."
    )

    try:
        report = await analyze_use_case.execute(time_range)
    except Exception as e:
        await loading_msg.edit_text(f"❌ Analyze failed: {e}", reply_markup=get_main_menu())

    await handle_report_callback(
        callback,
        time_range=time_range,
        report=report,
        report_type=ReportType.ANALYZE,
        formatter=formatter,
        notifier=notifier,
        loading_msg=loading_msg,
    )


@bot_router.callback_query(F.data.startswith("recent_"))
@inject
async def on_recent_period(
    callback: CallbackQuery,
    errors_use_case: FromDishka[RecentErrorsUseCase],
    formatter: FromDishka[ReportFormatter],
    notifier: FromDishka[Notifier],
    state: FSMContext,
) -> None:
    await state.set_state(BotStates.viewing_report)
    hours = int(callback.data.split("_")[1])
    time_range = TimeRange(hours)

    try:
        report = await errors_use_case.execute(time_range)
    except Exception as e:
        await callback.message.edit_text(
            f"❌ Fetching recent errors failed: {e}", reply_markup=get_main_menu()
        )

    await handle_report_callback(
        callback,
        time_range=time_range,
        report=report,
        report_type=ReportType.RECENT,
        formatter=formatter,
        notifier=notifier,
    )


@bot_router.callback_query(F.data.startswith("stats_"))
@inject
async def on_statistics_period(
    callback: CallbackQuery,
    statistics_use_case: FromDishka[StatisticsLogsUseCase],
    formatter: FromDishka[ReportFormatter],
    notifier: FromDishka[Notifier],
    state: FSMContext,
) -> None:
    await state.set_state(BotStates.viewing_report)
    await state.set_state(BotStates.viewing_report)
    hours = int(callback.data.split("_")[1])
    time_range = TimeRange(hours)

    try:
        report = await statistics_use_case.execute(time_range)
    except Exception as e:
        await callback.message.edit_text(
            f"❌ Fetching statistics failed: {e}", reply_markup=get_main_menu()
        )

    await handle_report_callback(
        callback,
        time_range=time_range,
        report=report,
        report_type=ReportType.STATS,
        formatter=formatter,
        notifier=notifier,
    )


@bot_router.callback_query(F.data == BotCallback.BACK_TO_MENU.value)
async def back_to_menu(callback: CallbackQuery, state: FSMContext) -> None:
    await callback.answer()
    current_state = await state.get_state()
    if current_state == BotStates.period_selection:
        await callback.message.edit_text("Choose an action:", reply_markup=get_main_menu())
    else:
        await callback.message.edit_text("Choose an action:", reply_markup=get_main_menu())

    await state.set_state(BotStates.main_menu)
