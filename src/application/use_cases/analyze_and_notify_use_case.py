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
from src.domain.entities.enums import ReportTemplate
from src.domain.entities.report import ErrorGroup, ReportData
from src.interfaces.bot.formatters.html_formatter import ReportFormatter
from src.responses import LLMAnalysisResult, LogsByErrorType, LogsSourceQueryResult

logger = getLogger(__name__)

# TODO: change HTML to markdown?


class AnalyzeLogsUseCase:
    def __init__(
        self,
        log_source: LogSource,
        notifier: Notifier,
        app_settings: AppSettings,
        llm_analyzer: LLMAnalyzer,
        formatter: ReportFormatter,
    ) -> None:
        self.log_source = log_source
        self.notifier = notifier
        self.app_settings = app_settings
        self.formatter = formatter
        self.llm_analyzer = llm_analyzer

    async def analyze_logs(self, hours: int) -> AnalysisResult:
        logger.info("Fetching recent error logs for analysis...")
        logs = await self.log_source.get_errors(hours)
        no_errors_result = await self._check_and_notify_no_errors(hours, len(logs))
        if no_errors_result:
            return no_errors_result

        logger.info(f"Found {len(logs)} error logs for last {hours}h")
        grouped = await self.log_source._group_errors_by_type(logs)

        logger.info(f"Analyzing {len(logs)} logs with {self.app_settings.llm_provider.provider}")
        analysis = await self.llm_analyzer.analyze(logs)

        logger.info(
            f"Analysis completed. Tokens: {analysis.input_tokens_used}/{analysis.output_tokens_used}"
        )

        report_obj = self.prepare_report_from_llm(analysis, grouped, hours)
        report_html = self.formatter.to_html(report_obj)
        return AnalysisResult(has_errors=True, report_html=report_html, hours=hours)

    async def get_recent_errors(self, hours: int) -> AnalysisResult:
        logs = await self.log_source.get_recent_errors(hours)

        no_errors_result = await self._check_and_notify_no_errors(hours, len(logs))
        if no_errors_result:
            return no_errors_result

        report_obj = self.prepare_report_recent_errors(logs, hours)
        report_html = self.formatter.to_html(report_obj, ReportTemplate.RECENT_LOGS)

        return AnalysisResult(has_errors=True, report_html=report_html, hours=hours)

    async def get_statistics(self, hours: int) -> AnalysisResult:
        logger.info(f"Fetching statistics for last {hours} h.")
        logs = await self.log_source.get_errors(hours)

        no_errors_result = await self._check_and_notify_no_errors(hours, len(logs))
        if no_errors_result:
            return no_errors_result

        grouped = await self.log_source._group_errors_by_type(logs)
        report_obj = self.prepare_report_statistics(logs, grouped, hours)

        report_html = self.formatter.to_html(
            report_obj,
            ReportTemplate.STATISTICS,
        )

        return AnalysisResult(
            has_errors=True,
            report_html=report_html,
            hours=hours,
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

    def prepare_report_recent_errors(
        self, recent_errors: LogsSourceQueryResult, hours: int
    ) -> ReportData:
        report_obj = ReportData(
            title=f"Recent logs for the last {hours} {format_hours(hours)}",
            time_range_hours=hours,
            total_errors=recent_errors.total_count,
            logs=recent_errors.logs,
        )
        return report_obj

    def prepare_report_statistics(
        self,
        logs: LogsSourceQueryResult,
        grouped: LogsByErrorType,
        hours: int,
    ) -> ReportData:
        groups = [
            ErrorGroup(error_type=group.error, count=len(group.logs))
            for group in grouped.logs_groups
        ]
        groups.sort(key=lambda x: x.count, reverse=True)

        return ReportData(
            title=f"📊 Statistics for the last {hours} {format_hours(hours)}",
            time_range_hours=hours,
            total_errors=len(logs),
            unique_types=len(grouped.logs_groups),
            groups=groups,
        )

    def prepare_report_from_llm(
        self, analysis: LLMAnalysisResult, grouped_logs: LogsByErrorType, hours: int
    ) -> ReportData:
        total_errors = sum(len(group.logs) for group in grouped_logs.logs_groups)
        groups = [
            ErrorGroup(error_type=group.error, count=len(group.logs))
            for group in grouped_logs.logs_groups
        ]
        report_obj = ReportData(
            title=f"Error report for the last {hours} {format_hours(hours)}",
            time_range_hours=hours,
            total_errors=total_errors,
            unique_types=len(grouped_logs.logs_groups),
            ai_analysis=analysis.analysis_text,
            provider=analysis.provider.value,
            tokens_in=analysis.input_tokens_used,
            tokens_out=analysis.output_tokens_used,
            groups=groups,
        )
        return report_obj

    async def _check_and_notify_no_errors(
        self, hours: int, logs_count: int
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
