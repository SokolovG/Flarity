from typing import Any

from aiogram.types import CallbackQuery
from aiogram_dialog import DialogManager

from src.interfaces.bot.entities import RecentSG


async def on_recent(callback: CallbackQuery, widget: Any, manager: DialogManager) -> None:
    await manager.start(RecentSG.period_selection)


async def on_recent_period_click(
    callback: CallbackQuery, widget: Any, manager: DialogManager
) -> None: ...
