from jinja2 import Environment, FileSystemLoader

from src.application.dto.analysis_report import AnalysisReport, ErrorGroup
from src.domain.entities.enums import ReportType
from src.domain.utils import format_time_range
from src.infrastructure.constants import (
    MAX_ERRORS_IN_ONE_REPORT,
    MAX_GROUPS_IN_REPORT,
    MAX_SYMBOLS_LOG_MSG,
)
from src.infrastructure.settings.report_settings import ReportSettings


class ReportFormatter:
    def __init__(self, report_settings: ReportSettings) -> None:
        self.env = Environment(
            loader=FileSystemLoader("resources/report_templates"), autoescape=True
        )
        self.report_settings = report_settings

    def to_html(
        self, report: AnalysisReport, report_type: ReportType, show_all_errors: bool | None = False
    ) -> str:
        template_name = self.report_settings.get_template(report_type)
        template = self.env.get_template(template_name)

        title = f"Error report for the last {report.time_range.hours} {format_time_range(report.time_range)}"
        total_errors = len(report.logs) if report.logs else 0
        unique_types = len(report.groups) if report.groups else 0

        ai_analysis = None
        provider = None
        tokens_in = None
        tokens_out = None

        if report.llm_analysis:
            ai_analysis = report.llm_analysis.analysis_text
            provider = report.llm_analysis.provider.value
            tokens_in = report.llm_analysis.input_tokens_used
            tokens_out = report.llm_analysis.output_tokens_used

        groups_list = None
        if report.groups:
            groups_list = [
                ErrorGroup(error_type=key, count=len(logs)) for key, logs in report.groups.items()
            ]

        return template.render(
            title=title,
            time_range_hours=report.time_range.hours,
            total_errors=total_errors,
            unique_types=unique_types,
            logs=report.logs,
            groups=groups_list,
            ai_analysis=ai_analysis,
            provider=provider,
            tokens_in=tokens_in,
            tokens_out=tokens_out,
            show_all_errors=show_all_errors,
            max_errors=MAX_ERRORS_IN_ONE_REPORT,
            max_symbols=MAX_SYMBOLS_LOG_MSG,
            max_groups=MAX_GROUPS_IN_REPORT,
        )
