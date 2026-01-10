from typing import Any

from aiogram_dialog import DialogManager
from dishka.integrations.aiogram import FromDishka
from dishka.integrations.aiogram_dialog import inject

from src.domain.entities.enums import ReportType
from src.interfaces.bot.formatters.html_formatter import ReportFormatter


@inject
async def stats_report_getter(
    dialog_manager: DialogManager, formatter: FromDishka[ReportFormatter], **kwargs: Any
) -> dict[str, str]:
    report = dialog_manager.dialog_data.get("report")
    html = formatter.to_html(report, ReportType.STATS)
    return {
        "report_html": html,
    }
