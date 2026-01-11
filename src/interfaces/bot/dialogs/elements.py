from aiogram.types import CallbackQuery
from aiogram_dialog import DialogManager, StartMode
from aiogram_dialog.widgets.kbd import Button

from src.interfaces.bot.core.states import MainSG


async def on_cancel(
    callback: CallbackQuery,
    widget: Button,
    manager: DialogManager,
) -> None:
    await manager.done()
    await manager.start(MainSG.menu, mode=StartMode.RESET_STACK)
