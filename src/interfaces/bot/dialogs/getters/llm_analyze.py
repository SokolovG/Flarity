from typing import Any

from aiogram_dialog import DialogManager
from dishka.integrations.aiogram import FromDishka
from dishka.integrations.aiogram_dialog import inject

from src.application.dto.analysis_report import AnalysisReport
from src.domain.entities.enums import ReportType
from src.interfaces.bot.formatters.html_formatter import ReportFormatter


@inject
async def analyze_report_getter(
    dialog_manager: DialogManager, formatter: FromDishka[ReportFormatter], **kwargs: Any
) -> dict[str, str]:
    report: AnalysisReport = dialog_manager.dialog_data.get("report")  # type: ignore
    html = formatter.to_html(report, ReportType.ANALYZE)
    return {
        "report_html": html,
    }


@inject
async def ask_llm_report_getter(
    dialog_manager: DialogManager, formatter: FromDishka[ReportFormatter], **kwargs: Any
) -> dict[str, str]:
    report: AnalysisReport = dialog_manager.dialog_data.get("report")  # type: ignore
    html = formatter.to_html(report, ReportType.ANSWER)
    return {
        "answer_html": html,
    }
