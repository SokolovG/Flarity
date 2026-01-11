from aiogram.types import CallbackQuery
from aiogram_dialog import DialogManager
from aiogram_dialog.widgets.kbd import Button

from src.interfaces.bot.states import MainSG


async def on_cancel(
    callback: CallbackQuery,
    widget: Button,
    manager: DialogManager,
) -> None:
    await manager.done()
    await manager.start(MainSG.menu)
