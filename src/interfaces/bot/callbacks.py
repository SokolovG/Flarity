from logging import getLogger

from aiogram import F
from aiogram.fsm.context import FSMContext
from aiogram.types import CallbackQuery
from dishka.integrations.aiogram import FromDishka, inject

from src.application.ports.notifier import Notifier
from src.application.use_cases.analyze_logs_use_case import AnalyzeLogsUseCase
from src.application.use_cases.get_recent_errors_use_case import RecentLogsUseCase
from src.application.use_cases.get_statistics_use_case import StatisticsLogsUseCase
from src.core.settings.app_settings import AppSettings
from src.core.utils import format_time_range, get_settings_for_bot
from src.domain.value_objects.time_range import TimeRange
from src.interfaces.bot.entities import BotAction, BotCallback, BotStates
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
    info = get_settings_for_bot(
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
    errors_use_case: FromDishka[RecentLogsUseCase],
    statistics_use_case: FromDishka[StatisticsLogsUseCase],
    notifier: FromDishka[Notifier],
    state: FSMContext,
) -> None:
    await state.set_state(BotStates.viewing_report)
    await _handle_analysis(
        callback=callback,
        analyze_use_case=analyze_use_case,
        errors_use_case=errors_use_case,
        statistics_use_case=statistics_use_case,
        notifier=notifier,
        action=BotAction.ANALYZE,
    )


@bot_router.callback_query(F.data.startswith("recent_"))
@inject
async def on_recent_period(
    callback: CallbackQuery,
    analyze_use_case: FromDishka[AnalyzeLogsUseCase],
    errors_use_case: FromDishka[RecentLogsUseCase],
    statistics_use_case: FromDishka[StatisticsLogsUseCase],
    notifier: FromDishka[Notifier],
    state: FSMContext,
) -> None:
    await state.set_state(BotStates.viewing_report)
    await _handle_analysis(
        callback=callback,
        analyze_use_case=analyze_use_case,
        errors_use_case=errors_use_case,
        statistics_use_case=statistics_use_case,
        notifier=notifier,
        action=BotAction.RECENT,
    )


@bot_router.callback_query(F.data.startswith("stats_"))
@inject
async def on_statistics_period(
    callback: CallbackQuery,
    analyze_use_case: FromDishka[AnalyzeLogsUseCase],
    errors_use_case: FromDishka[RecentLogsUseCase],
    statistics_use_case: FromDishka[StatisticsLogsUseCase],
    notifier: FromDishka[Notifier],
    state: FSMContext,
) -> None:
    await state.set_state(BotStates.viewing_report)
    await _handle_analysis(
        callback=callback,
        analyze_use_case=analyze_use_case,
        errors_use_case=errors_use_case,
        statistics_use_case=statistics_use_case,
        notifier=notifier,
        action=BotAction.STATS,
    )


async def _handle_analysis(
    callback: CallbackQuery,
    analyze_use_case: AnalyzeLogsUseCase,
    errors_use_case: RecentLogsUseCase,
    statistics_use_case: StatisticsLogsUseCase,
    notifier: Notifier,
    action: BotAction,
) -> None:
    hours = int(callback.data.split("_")[1])
    time_range = TimeRange(hours)

    await callback.answer()

    loading_msg = await callback.message.edit_text(
        f"{action} logs for last {hours} {format_time_range(time_range)}\n"
        f"{'This may take up to 30 seconds.' if action != BotAction.RECENT else ''}"
    )

    try:
        match action:
            case BotAction.RECENT:
                result = await errors_use_case.execute(time_range)
            case BotAction.ANALYZE:
                result = await analyze_use_case.execute(time_range)
            case BotAction.STATS:
                result = await statistics_use_case.execute(time_range)

        if not result.has_errors:
            await loading_msg.edit_text("No errors", reply_markup=get_main_menu())
            return

        # await loading_msg.delete()
        await notifier.send(
            result.llm_analysis.report_html,
            chat_id=callback.message.chat.id,
        )
        await callback.message.answer("Choose an action:", reply_markup=get_main_menu())

    except Exception as e:
        logger.exception(f"Analysis failed: {e}")
        await loading_msg.edit_text(f"❌ {action} failed: {e}", reply_markup=get_main_menu())


@bot_router.callback_query(F.data == BotCallback.BACK_TO_MENU.value)
async def back_to_menu(callback: CallbackQuery, state: FSMContext) -> None:
    await callback.answer()
    current_state = await state.get_state()
    if current_state == BotStates.period_selection:
        await callback.message.edit_text("Choose an action:", reply_markup=get_main_menu())
    else:
        await callback.message.edit_text("Choose an action:", reply_markup=get_main_menu())

    await state.set_state(BotStates.main_menu)
