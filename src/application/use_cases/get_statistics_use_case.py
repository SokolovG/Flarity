from src.application.ports.llm_analyzer import LLMAnalyzer
from src.application.ports.log_source import LogSource
from src.core.utils import format_time_range
from src.domain.entities.analysis_report import AnalysisReport, ErrorGroup, ReportData
from src.domain.services.error_grouper import ErrorGrouper
from src.domain.value_objects.time_range import TimeRange
from src.responses.logs_base_responses import LogsByErrorType, LogsSourceQueryResult


class StatisticsLogsUseCase:
    def __init__(self, log_source: LogSource, llm: LLMAnalyzer, grouper: ErrorGrouper) -> None:
        self.log_source = log_source
        self.llm = llm
        self.grouper = grouper

    async def execute(self, time_range: TimeRange) -> AnalysisReport:
        logs = await self.log_source.get_errors(time_range)

        if not logs:
            return AnalysisReport(has_errors=False, time_range=time_range)

        groups = self.grouper.group_by_category(logs)

        return AnalysisReport(has_errors=True, time_range=time_range, logs=logs, groups=groups)

    def _prepare_report_statistics(
        self,
        logs: LogsSourceQueryResult,
        grouped: LogsByErrorType,
        time_range: TimeRange,
    ) -> ReportData:
        groups = [
            ErrorGroup(error_type=group.error, count=len(group.logs))
            for group in grouped.logs_groups
        ]
        groups.sort(key=lambda x: x.count, reverse=True)

        return ReportData(
            title=f"📊 Statistics for the last {time_range} {format_time_range(time_range)}",
            time_range_time_range=time_range,
            total_errors=len(logs),
            unique_types=len(grouped.logs_groups),
            groups=groups,
        )
