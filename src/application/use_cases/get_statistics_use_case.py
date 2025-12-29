from src.application.dto.analysis_report import AnalysisReport
from src.application.ports.llm_analyzer import LLMAnalyzer
from src.application.ports.log_source import LogSource
from src.domain.services.error_grouper import ErrorGrouper
from src.domain.value_objects.time_range import TimeRange
from src.infrastructure.decorators import log_calls


class StatisticsLogsUseCase:
    def __init__(self, log_source: LogSource, llm: LLMAnalyzer, grouper: ErrorGrouper) -> None:
        self.log_source = log_source
        self.llm = llm
        self.grouper = grouper

    @log_calls
    async def execute(self, time_range: TimeRange) -> AnalysisReport:
        logs = await self.log_source.get_errors(time_range)

        if not logs:
            return AnalysisReport(has_errors=False, time_range=time_range)

        groups = self.grouper.group_by_category(logs)

        return AnalysisReport(has_errors=True, time_range=time_range, logs=logs, groups=groups)
