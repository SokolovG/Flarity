from typing import Any

from aiogram_dialog import DialogManager

from src.infrastructure.settings.app_settings import AppSettings
from src.interfaces.bot.formatters.text_formatter import BotTextFormatter


async def help_getter(
    dialog_manager: DialogManager,
    **kwargs: Any,
) -> dict[str, str]:
    help_info = BotTextFormatter.format_help()
    return {
        "help_info": help_info,
    }
