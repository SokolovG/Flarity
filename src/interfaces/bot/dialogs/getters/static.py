from typing import Any

from aiogram_dialog import DialogManager
from dishka.integrations.aiogram import FromDishka
from dishka.integrations.aiogram_dialog import inject

from src.infrastructure.settings.app_settings import AppSettings
from src.interfaces.bot.formatters.text_formatter import BotTextFormatter


@inject
async def settings_getter(
    dialog_manager: DialogManager,
    app_settings: FromDishka[AppSettings],
    **kwargs: Any,
) -> dict[str, str]:
    settings_info = BotTextFormatter.format_settings(app_settings)
    return {
        "settings_info": settings_info,
    }


async def help_getter(
    dialog_manager: DialogManager,
    **kwargs: Any,
) -> dict[str, str]:
    help_info = BotTextFormatter.format_help()
    return {
        "help_info": help_info,
    }
