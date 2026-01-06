from jinja2 import Environment, FileSystemLoader

from src.application.dto.analysis_report import AnalysisReport, ErrorGroup
from src.application.dto.analysis_result import LLMAnalysisResult
from src.domain.entities.enums import ReportType
from src.infrastructure.constants import (
    BASE_DIR,
    MAX_ERRORS_IN_ONE_REPORT,
    MAX_GROUPS_IN_REPORT,
    MAX_SYMBOLS_LOG_MSG,
)
from src.infrastructure.settings.report_settings import ReportSettings

TEMPLATES_DIR = BASE_DIR / "resources" / "templates"


class ReportFormatter:
    def __init__(self, report_settings: ReportSettings) -> None:
        self.env = Environment(loader=FileSystemLoader(TEMPLATES_DIR), autoescape=True)
        self.report_settings = report_settings

    def to_html(
        self, report: AnalysisReport, report_type: ReportType, show_all_errors: bool | None = False
    ) -> str:
        template_name = self.report_settings.get_template(report_type)
        template = self.env.get_template(template_name)

        title = f"Error report for the last {report.time_range.hour_and_unit}"
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

        result = template.render(
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
        if not result or len(result.strip()) < 10:
            raise ValueError(
                f"Template {template_name} produced empty or invalid output. "
                "Check template syntax and data."
            )

        return result

    def format_llm_answer(self, answer: LLMAnalysisResult, report_type: ReportType) -> str:
        template_name = self.report_settings.get_template(report_type)
        template = self.env.get_template(template_name)

        return template.render(
            answer=answer.analysis_text,
            provider=answer.provider.value,
            tokens_in=answer.input_tokens_used,
            tokens_out=answer.output_tokens_used,
        )
