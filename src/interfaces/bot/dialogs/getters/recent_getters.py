from typing import Any

from aiogram_dialog import DialogManager
from dishka.integrations.aiogram import FromDishka
from dishka.integrations.aiogram_dialog import inject

from src.application.dto.analysis_report import AnalysisReport
from src.domain.entities.enums import ReportType
from src.infrastructure.constants import MAX_ERRORS_IN_ONE_REPORT
from src.interfaces.bot.formatters.html_formatter import ReportFormatter


@inject
async def recent_report_getter(
    dialog_manager: DialogManager, formatter: FromDishka[ReportFormatter], **kwargs: Any
) -> dict[str, Any]:
    report: AnalysisReport = dialog_manager.dialog_data.get("report")

    total = len(report.logs) if report.logs else 0
    has_more = total > MAX_ERRORS_IN_ONE_REPORT

    html = formatter.to_html(report, ReportType.RECENT, show_all_errors=False)
    return {
        "report_html": html,
        "total_errors": total,
        "has_more_errors": has_more,
    }
