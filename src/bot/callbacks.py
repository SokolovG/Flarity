from aiogram import F
from aiogram.types import CallbackQuery
from dishka.integrations.aiogram import FromDishka

from src.bot.keyboards import get_analysis_options, get_back_to_menu_button, get_main_menu
from src.bot.router import bot_router
from src.services import LogAnalysisService


@bot_router.callback_query(F.data.startwith("analyze"))
async def on_analyze_period(
    callback: CallbackQuery, service: FromDishka[LogAnalysisService]
) -> None:
    hours = int(callback.data.split("_")[1])
    await callback.answer()

    await callback.message.edit_text(
        f"🔄 Analyzing logs for last {hours}h...\nThis may take up to 30 seconds."
    )

    try:
        text = await service.analyze_logs(hours=hours, msg_without_errors=True)

        await callback.message.edit_text(text, parse_mode="HTML")

    except Exception as e:
        await callback.message.edit_text(f"❌ Analysis failed: {e}")
    await callback.answer()
    await callback.message.edit_text(
        f"🔄 Analyzing logs for last {hours}h...\nThis may take up to 30 seconds.",
        reply_markup=get_back_to_menu_button(),
    )


@bot_router.callback_query(F.data == "llm_analysis")
async def on_llm_analysis(callback: CallbackQuery) -> None:
    await callback.answer()
    await callback.message.answer("Choose analysis period:", reply_markup=get_analysis_options())


@bot_router.callback_query(F.data == "back_to_menu")
async def back_to_menu(callback: CallbackQuery) -> None:
    await callback.answer()
    await callback.message.edit_text("Choose an action:", reply_markup=get_main_menu())
