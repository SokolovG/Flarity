from aiogram import F
from aiogram.types import CallbackQuery

from src.bot.keyboards import get_analysis_options
from src.bot.router import bot_router


@bot_router.callback_query(F.data == "llm_analysis")
async def on_llm_analysis(callback: CallbackQuery) -> None:
    await callback.answer()
    await callback.message.answer("Choose analysis period:", reply_markup=get_analysis_options())
