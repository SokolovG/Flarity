from logging import getLogger

from aiogram.filters import Command, CommandStart, StateFilter
from aiogram.types import Message
from aiogram_dialog import DialogManager, LaunchMode, StartMode

from src.interfaces.bot.core.constants import EASTER_EGGS_WORT_LIST
from src.interfaces.bot.core.router import bot_router
from src.interfaces.bot.core.states import (
    AnalyzeSG,
    BugSG,
    HelpSG,
    MainSG,
    RecentSG,
    SettingsSG,
    StatsSG,
)

logger = getLogger(__name__)


@bot_router.message(CommandStart())
async def cmd_start(message: Message, dialog_manager: DialogManager) -> None:
    await dialog_manager.start(MainSG.menu, mode=StartMode.RESET_STACK)


@bot_router.message(Command("analyze"))
async def cmd_analyze(message: Message, dialog_manager: DialogManager) -> None:
    await dialog_manager.start(AnalyzeSG.period_selection, mode=StartMode.RESET_STACK)


@bot_router.message(Command("recent"))
async def cmd_recent(message: Message, dialog_manager: DialogManager) -> None:
    await dialog_manager.start(RecentSG.period_selection, mode=StartMode.RESET_STACK)


@bot_router.message(Command("stats"))
async def cmd_stats(message: Message, dialog_manager: DialogManager) -> None:
    await dialog_manager.start(StatsSG.period_selection, mode=StartMode.RESET_STACK)


@bot_router.message(Command("settings"))
async def cmd_settings(message: Message, dialog_manager: DialogManager) -> None:
    await dialog_manager.start(SettingsSG.viewing_data, mode=StartMode.RESET_STACK)


@bot_router.message(Command("bug"))
async def cmd_bug(message: Message, dialog_manager: DialogManager) -> None:
    await dialog_manager.start(BugSG.reporting, mode=StartMode.RESET_STACK)


@bot_router.message(Command("help"))
async def cmd_help(message: Message, dialog_manager: DialogManager) -> None:
    await dialog_manager.start(HelpSG.viewing_data, mode=StartMode.RESET_STACK)


@bot_router.message(Command("menu"))
async def cmd_menu(message: Message, dialog_manager: DialogManager) -> None:
    await dialog_manager.start(MainSG.menu, mode=StartMode.RESET_STACK)


@bot_router.message(StateFilter(None))
async def handle_unknown_message(message: Message, dialog_manager: DialogManager) -> None:
    if message.text in EASTER_EGGS_WORT_LIST:
        match message.text:
            case "ogonek":
                await message.answer("https://ogonek.app")
            case "author":
                await message.answer("https://github.com/SokolovG")

        return

    await message.answer("I don't understand you! Please use /help")
    await dialog_manager.start(MainSG.menu, mode=StartMode.RESET_STACK)
