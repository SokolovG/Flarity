from typing import Any

from aiogram_dialog import DialogManager
from dishka.integrations.aiogram import FromDishka
from dishka.integrations.aiogram_dialog import inject

from src.domain.entities.enums import ReportType
from src.infrastructure.settings.app_settings import AppSettings
from src.interfaces.bot.formatters.text_formatter import BotTextFormatter


@inject
async def settings_getter(
    dialog_manager: DialogManager,
    formatter: FromDishka[BotTextFormatter],
    app_settings: AppSettings,
    **kwargs: Any,
) -> dict[str, str]:
    settings_info = formatter.format_settings(app_settings)
    return {
        "settings_info": settings_info,
    }
