from typing import Any

from aiogram.types import CallbackQuery
from aiogram_dialog import DialogManager

from src.interfaces.bot.entities import StatsSG


async def on_stats(callback: CallbackQuery, widget: Any, manager: DialogManager) -> None:
    await manager.start(StatsSG.period_selection)


async def on_stats_period_click(
    callback: CallbackQuery, widget: Any, manager: DialogManager
) -> None: ...
