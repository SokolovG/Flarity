from aiogram.filters import CommandStart
from aiogram.types import Message
from aiogram_dialog import DialogManager

from src.interfaces.bot.entities import MainSG
from src.interfaces.bot.router import bot_router


@bot_router.message(CommandStart())
async def cmd_start(message: Message, dialog_manager: DialogManager) -> None:
    await dialog_manager.start(MainSG.menu)
