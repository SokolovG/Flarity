from src.application.ports.llm_analyzer import LLMAnalyzer
from src.application.ports.log_source import LogSource
from src.application.ports.notifier import Notifier
from src.core.utils import format_time_range
from src.domain.entities.analysis_report import AnalysisReport, ReportData
from src.domain.value_objects.time_range import TimeRange
from src.responses.logs_base_responses import LogsSourceQueryResult


class RecentLogsUseCase:
    def __init__(
        self,
        log_source: LogSource,
        llm: LLMAnalyzer,
    ) -> None:
        self.log_source = log_source
        self.llm = llm

    async def execute(self, time_range: TimeRange) -> AnalysisReport:
        logs = await self.log_source.get_errors(time_range)

        if not logs:
            return AnalysisReport(has_errors=False, time_range=time_range)

        return AnalysisReport(
            has_errors=True,
            time_range=time_range,
            logs=logs,
        )

    def _prepare_report_recent_errors(
        self, recent_errors: LogsSourceQueryResult, time_range: TimeRange
    ) -> ReportData:
        report_obj = ReportData(
            title=f"Recent logs for the last {time_range} {format_time_range(time_range)}",
            time_range_time_range=time_range,
            total_errors=recent_errors.total_count,
            logs=recent_errors.logs,
        )
        return report_obj
