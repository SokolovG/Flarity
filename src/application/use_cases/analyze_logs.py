from src.application.dto.analysis_result import AnalysisResult
from src.application.ports.llm_analyzer import LLMAnalyzer
from src.domain.services.base_services import LogSourceService
from src.domain.services.error_grouper import ErrorGrouper
from src.domain.value_objects.time_range import TimeRange


class AnalyzeLogsUseCase:
    def __init__(
        self,
        log_source: LogSourceService,
        llm_analyzer: LLMAnalyzer,
        error_grouper: ErrorGrouper,
    ):
        self.log_source = log_source
        self.llm = llm_analyzer
        self.grouper = error_grouper

    async def execute(self, time_range: TimeRange) -> AnalysisResult:
        logs = await self.log_source.get_errors(time_range)
        if not logs:
            return AnalysisResult.no_errors(time_range)

        groups = self.grouper.group_by_category(logs)

        analysis = await self.llm.analyze(logs)

        return AnalysisResult(
            has_errors=True,
            time_range=time_range,
            groups=groups,
            analysis=analysis,
        )
