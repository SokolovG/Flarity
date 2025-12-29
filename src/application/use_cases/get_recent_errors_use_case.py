from src.application.dto.analysis_report import AnalysisReport
from src.application.ports.llm_analyzer import LLMAnalyzer
from src.application.ports.log_source import LogSource
from src.domain.value_objects.time_range import TimeRange
from src.infrastructure.decorators import log_calls


class RecentErrorsUseCase:
    def __init__(
        self,
        log_source: LogSource,
        llm: LLMAnalyzer,
    ) -> None:
        self.log_source = log_source
        self.llm = llm

    @log_calls
    async def execute(self, time_range: TimeRange) -> AnalysisReport:
        logs = await self.log_source.get_errors(time_range)

        if not logs:
            return AnalysisReport(has_errors=False, time_range=time_range)

        return AnalysisReport(
            has_errors=True,
            time_range=time_range,
            logs=logs,
        )
