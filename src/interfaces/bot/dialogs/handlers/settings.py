from typing import Any

from aiogram.types import CallbackQuery
from aiogram_dialog import DialogManager

from src.interfaces.bot.entities import SettingsSG


async def on_settings(callback: CallbackQuery, widget: Any, manager: DialogManager) -> None:
    await manager.start(SettingsSG.viewing_data)
