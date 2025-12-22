from logging import getLogger

from aiogram import F
from aiogram.types import CallbackQuery
from dishka.integrations.aiogram import FromDishka, inject

from src.bot.keyboards import (
    get_analysis_options,
    get_back_to_menu_button,
    get_main_menu,
    get_recent_options,
)
from src.bot.router import bot_router
from src.core.settings.app_settings import AppSettings
from src.core.utils import format_hours, get_settings_for_bot
from src.services import LogAnalysisService

logger = getLogger(__name__)


@bot_router.callback_query(F.data.startswith("analyze_"))
@inject
async def on_analyze_period(
    callback: CallbackQuery, service: FromDishka[LogAnalysisService]
) -> None:
    await _handle_analysis(callback, service, with_llm=True)


@bot_router.callback_query(F.data == "llm_analysis")
async def on_llm_analysis(callback: CallbackQuery) -> None:
    await callback.answer()
    await callback.message.answer("Choose analysis period:", reply_markup=get_analysis_options())


@bot_router.callback_query(F.data == "recent")
async def on_recent_errors(callback: CallbackQuery) -> None:
    await callback.answer()
    await callback.message.answer("Choose analysis period:", reply_markup=get_recent_options())


@bot_router.callback_query(F.data == "statistics")
async def statistics(callback: CallbackQuery) -> None:
    await callback.answer()


@bot_router.callback_query(F.data.startswith("recent_"))
@inject
async def on_recent_period(
    callback: CallbackQuery, service: FromDishka[LogAnalysisService]
) -> None:
    await _handle_analysis(callback, service, with_llm=False)


async def _handle_analysis(
    callback: CallbackQuery,
    service: LogAnalysisService,
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

        await loading_msg.edit_text(
            result.report_html, parse_mode="HTML", reply_markup=get_back_to_menu_button()
        )

    except Exception as e:
        logger.exception(f"Analysis failed: {e}")
        await loading_msg.edit_text(
            f"❌ {action} failed: {e}", reply_markup=get_back_to_menu_button()
        )


@bot_router.callback_query(F.data == "back_to_menu")
async def back_to_menu(callback: CallbackQuery) -> None:
    await callback.answer()
    await callback.message.edit_text("Choose an action:", reply_markup=get_main_menu())


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
    await callback.message.answer(info, reply_markup=get_back_to_menu_button())
