from typing import Any

import msgspec
from aiogram_dialog import DialogManager
from dishka.integrations.aiogram import FromDishka
from dishka.integrations.aiogram_dialog import inject

from src.application.dto.analysis_report import AnalysisReport
from src.domain.constants import MAX_ERRORS_IN_ONE_REPORT
from src.domain.entities.enums import ReportType
from src.interfaces.bot.formatters.html_formatter import ReportFormatter


@inject
async def recent_all_getter(
    dialog_manager: DialogManager, formatter: FromDishka[ReportFormatter], **kwargs: Any
) -> dict[str, str]:
    report: AnalysisReport = dialog_manager.dialog_data.get(
        "report"
    )  # ty:ignore[invalid-assignment]
    html = formatter.to_html(report, ReportType.RECENT, show_all_errors=True)

    return {
        "report_html_all": html,
    }


@inject
async def recent_report_getter(
    dialog_manager: DialogManager, formatter: FromDishka[ReportFormatter], **kwargs: Any
) -> dict[str, Any]:
    report_dict = dialog_manager.dialog_data.get("report")
    report = msgspec.convert(report_dict, type=AnalysisReport)

    total = len(report.logs) if report.logs else 0
    has_more = total > MAX_ERRORS_IN_ONE_REPORT

    html = formatter.to_html(report, ReportType.RECENT, show_all_errors=False)
    return {
        "report_html": html,
        "total_errors": total,
        "has_more_errors": has_more,
    }
