import asyncio
from logging import getLogger

from src.application.dto.analysis_result import AnalysisResult
from src.application.ports.llm_analyzer import LLMAnalyzer
from src.application.ports.log_source import LogSource
from src.application.ports.notifier import Notifier
from src.core.decorators import retry
from src.core.exceptions import ServiceNotReadyError
from src.core.settings.app_settings import AppSettings
from src.core.utils import format_hours
from src.domain.entities.report import ErrorGroup, ReportData
from src.domain.services.error_grouper import ErrorGrouper
from src.domain.value_objects.time_range import TimeRange
from src.interfaces.bot.formatters.html_formatter import ReportFormatter

logger = getLogger(__name__)

# TODO: change HTML to markdown?


class AnalyzeLogsUseCase:
    def __init__(
        self,
        log_source: LogSource,
        notifier: Notifier,
        app_settings: AppSettings,
        llm: LLMAnalyzer,
        formatter: ReportFormatter,
        error_grouper: ErrorGrouper,
    ) -> None:
        self.log_source = log_source
        self.notifier = notifier
        self.app_settings = app_settings
        self.formatter = formatter
        self.llm = llm
        self.groupper = error_grouper

    async def execute(self, time_range: TimeRange) -> AnalysisResult:
        logs = await self.log_source.get_errors(time_range)
        if not logs:
            return AnalysisResult(
                has_errors=False,
                report_html=f"✅ No errors found in the last {time_range.hours} h",
                hours=time_range.hours,
            )

        groups = await self.log_source._group_errors_by_type(logs)
        analysis = await self.llm.analyze(logs)

        report_data = ReportData(
            title=f"Error report for the last {time_range.hours}h",
            time_range_hours=time_range.hours,
            total_errors=len(logs),
            unique_types=len(groups),
            ai_analysis=analysis.analysis_text,
            provider=analysis.provider.value,
            tokens_in=analysis.input_tokens_used,
            tokens_out=analysis.output_tokens_used,
            groups=[ErrorGroup(error_type=k, count=len(v)) for k, v in groups.items()],
        )

        report_html = self.formatter.to_html(report_data)
        return AnalysisResult(
            has_errors=True,
            report_html=report_html,
            hours=time_range.hours,
        )

    @retry(max_attempts=5, backoff=10.0)
    async def check_readiness(self) -> bool:
        coros = (self.log_source.check_readiness(),)

        loki_ready = await asyncio.gather(*coros, return_exceptions=True)
        services = {
            "Loki": loki_ready,
        }

        not_ready: list = []
        for service_name, result in services.items():
            if isinstance(result, Exception):
                logger.error(f"{service_name} check failed: {result}")
                not_ready.append(service_name)
            elif not result:
                logger.warning(f"{service_name} is not ready")
                not_ready.append(service_name)

        if not_ready:
            raise ServiceNotReadyError(f"Services not ready: {', '.join(not_ready)}")

        logger.info("All services are ready!")
        return True

    async def _check_and_notify_no_errors(
        self, hours: TimeRange, logs_count: int
    ) -> AnalysisResult | None:
        if logs_count == 0:
            msg = f"✅ No errors found in the last {hours} {format_hours(hours)}"
            result = AnalysisResult(
                has_errors=False,
                report_html=msg,
                hours=hours,
            )
            return result
        return None
