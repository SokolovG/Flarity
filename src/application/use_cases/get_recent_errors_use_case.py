from src.application.dto.analysis_result import AnalysisResult
from src.application.ports.llm_analyzer import LLMAnalyzer
from src.application.ports.log_source import LogSource
from src.application.ports.notifier import Notifier
from src.core.settings.app_settings import AppSettings
from src.core.utils import format_hours
from src.domain.entities.enums import ReportTemplate
from src.domain.entities.report import ReportData
from src.domain.value_objects.time_range import TimeRange
from src.interfaces.bot.formatters.html_formatter import ReportFormatter
from src.responses.logs_base_responses import LogsSourceQueryResult


class RecentLogsUseCase:
    def __init__(
        self,
        log_source: LogSource,
        notifier: Notifier,
        app_settings: AppSettings,
        llm: LLMAnalyzer,
        formatter: ReportFormatter,
    ) -> None:
        self.log_source = log_source
        self.notifier = notifier
        self.app_settings = app_settings
        self.formatter = formatter
        self.llm = llm

    async def execute(self, hours: TimeRange) -> AnalysisResult:
        logs = await self.log_source.get_recent_errors(hours)

        no_errors_result = await self._check_and_notify_no_errors(hours, len(logs))
        if no_errors_result:
            return no_errors_result

        report_obj = self._prepare_report_recent_errors(logs, hours)
        report_html = self.formatter.to_html(report_obj, ReportTemplate.RECENT_LOGS)

        return AnalysisResult(has_errors=True, report_html=report_html, hours=hours)

    def _prepare_report_recent_errors(
        self, recent_errors: LogsSourceQueryResult, hours: TimeRange
    ) -> ReportData:
        report_obj = ReportData(
            title=f"Recent logs for the last {hours} {format_hours(hours)}",
            time_range_hours=hours,
            total_errors=recent_errors.total_count,
            logs=recent_errors.logs,
        )
        return report_obj
