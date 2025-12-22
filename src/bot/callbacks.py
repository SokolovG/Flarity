from logging import getLogger

from aiogram import F
from aiogram.fsm.context import FSMContext
from aiogram.types import CallbackQuery
from dishka.integrations.aiogram import FromDishka, inject

from src.bot.keyboards import (
    get_analysis_options,
    get_main_menu,
    get_recent_options,
)
from src.bot.router import bot_router
from src.bot.states import BotStates
from src.core.settings.app_settings import AppSettings
from src.core.utils import format_hours, get_settings_for_bot
from src.services import LogAnalysisService
from src.services.notification_service import NotificationService

logger = getLogger(__name__)


@bot_router.callback_query(F.data.startswith("analyze_"))
@inject
async def on_analyze_period(
    callback: CallbackQuery,
    service: FromDishka[LogAnalysisService],
    notification_service: FromDishka[NotificationService],
    state: FSMContext,
) -> None:
    await state.set_state(BotStates.viewing_report)
    await _handle_analysis(callback, with_llm=True, service=service, notifier=notification_service)


@bot_router.callback_query(F.data == "llm_analysis")
async def on_llm_analysis(callback: CallbackQuery, state: FSMContext) -> None:
    await callback.answer()
    await state.set_state(BotStates.period_selection)
    await callback.message.answer("Choose analysis period:", reply_markup=get_analysis_options())


@bot_router.callback_query(F.data == "recent")
async def on_recent_errors(callback: CallbackQuery, state: FSMContext) -> None:
    await callback.answer()
    await state.set_state(BotStates.period_selection)
    await callback.message.answer("Choose period:", reply_markup=get_recent_options())


@bot_router.callback_query(F.data == "statistics")
async def statistics(callback: CallbackQuery) -> None:
    # send via await notifier.send_message()
    await callback.answer()


@bot_router.callback_query(F.data.startswith("recent_"))
@inject
async def on_recent_period(
    callback: CallbackQuery,
    service: FromDishka[LogAnalysisService],
    notification_service: FromDishka[NotificationService],
    state: FSMContext,
) -> None:
    await state.set_state(BotStates.viewing_report)
    await _handle_analysis(callback, with_llm=False, service=service, notifier=notification_service)


async def _handle_analysis(
    callback: CallbackQuery,
    service: LogAnalysisService,
    notifier: NotificationService,
    with_llm: bool,
) -> None:
    hours = int(callback.data.split("_")[1])

    action = "Analyzing" if with_llm else "Fetching"
    await callback.answer()

    loading_msg = await callback.message.edit_text(
        f"{action} logs for last {hours} {format_hours(hours)}\n"
        f"{'This may take up to 30 seconds.' if with_llm else ''}"
    )

    try:
        if with_llm:
            result = await service.analyze_logs(hours=hours)
        else:
            result = await service.get_recent_errors(hours=hours)

        if result.has_errors:
            await notifier.send_message(result.report_html)
            await callback.answer(text="", reply_markup=get_main_menu())
        else:
            await callback.message.edit_text(result.report_html)
            await callback.message.answer("", reply_markup=get_main_menu())

    except Exception as e:
        logger.exception(f"Analysis failed: {e}")
        await loading_msg.edit_text(f"❌ {action} failed: {e}", reply_markup=get_main_menu())


@bot_router.callback_query(F.data == "back_to_menu")
async def back_to_menu(callback: CallbackQuery, state: FSMContext) -> None:
    await callback.answer()
    current_state = await state.get_state()
    if current_state == BotStates.period_selection:
        await callback.message.edit_text("Choose an action:", reply_markup=get_main_menu())
    else:
        await callback.message.answer("Choose an action:", reply_markup=get_main_menu())

    await state.set_state(BotStates.main_menu)


@bot_router.callback_query(F.data == "settings")
@inject
async def settings(callback: CallbackQuery, app_settings: FromDishka[AppSettings]) -> None:
    await callback.answer()
    info = get_settings_for_bot(
        provider=app_settings.llm_provider.provider,
        model=app_settings.llm.model,
        schedule_hourse=app_settings.schedule_interval_hours,
        schedule_enabled=app_settings.schedule_enabled,
    )
    await callback.message.answer(info, reply_markup=get_main_menu(), parse_mode="HTML")
