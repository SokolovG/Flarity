from src.application.dto.analysis_report import AnalysisReport
from src.application.ports.llm_analyzer import LLMAnalyzer
from src.application.ports.log_source import LogSource
from src.domain.entities.log_entry import LogEntry
from src.domain.services.error_grouper import ErrorGrouper
from src.domain.value_objects.time_range import TimeRange
from src.infrastructure.constants import (
    RATE_LIMIT_ANALYZE_CALLS,
    RATE_LIMIT_ANALYZE_PERIOD,
    RATE_LIMITER_ANALYZE_PREFIX,
)
from src.infrastructure.decorators import log_calls
from src.infrastructure.rate_limiter import RateLimiter


class AnalyzeLogsUseCase:
    def __init__(
        self,
        log_source: LogSource,
        llm_analyzer: LLMAnalyzer,
        error_grouper: ErrorGrouper,
        limiter: RateLimiter,
    ):
        self.log_source = log_source
        self.llm = llm_analyzer
        self.grouper = error_grouper
        self.limiter = limiter

    @log_calls
    async def execute(self, time_range: TimeRange, user_id: str | None = None) -> AnalysisReport:
        logs = await self.log_source.get_errors(time_range)

        if not logs:
            return AnalysisReport(has_errors=False, time_range=time_range)

        if user_id:
            lock = self.limiter.acquire_user_lock(user_id)
            async with lock:
                await self.limiter.check_limit(
                    user_id,
                    prefix=RATE_LIMITER_ANALYZE_PREFIX,
                    calls=RATE_LIMIT_ANALYZE_CALLS,
                    period=RATE_LIMIT_ANALYZE_PERIOD,
                )
                return await self._analyze(time_range, logs)
        else:
            return await self._analyze(time_range, logs)

    async def _analyze(self, time_range: TimeRange, logs: list[LogEntry]) -> AnalysisReport:
        groups = self.grouper.group_by_category(logs)
        analysis = await self.llm.analyze(logs)

        return AnalysisReport(
            messages=analysis.messages,
            has_errors=True,
            time_range=time_range,
            logs=logs,
            groups=groups,
            llm_analysis=analysis,
        )
