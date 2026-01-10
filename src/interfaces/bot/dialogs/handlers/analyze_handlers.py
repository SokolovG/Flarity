from typing import Any

from aiogram.types import CallbackQuery
from aiogram_dialog import DialogManager

from src.interfaces.bot.entities import AnalyzeSG


async def on_analyze(callback: CallbackQuery, widget: Any, manager: DialogManager) -> None:
    await manager.start(AnalyzeSG.period_selection)


async def on_analyze_period_click(
    callback: CallbackQuery, widget: Any, manager: DialogManager
) -> None: ...
