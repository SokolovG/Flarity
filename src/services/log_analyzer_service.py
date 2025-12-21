import asyncio
from logging import getLogger

from src.core.decorators import retry
from src.core.settings.app_settings import AppSettings
from src.entities.enums import ReportTemplate
from src.entities.report import ErrorGroup, ReportData
from src.exceptions import ServiceNotReadyError
from src.responses.llm_base_responses import LLMAnalysisResult
from src.responses.logs_base_responses import LogsByErrorType, LogsSourceQueryResult
from src.services import LLMService, LogSourceService
from src.services.notification_service import NotificationService
from src.services.report_formatter_service import ReportFormatter

logger = getLogger(__name__)


class LogAnalysisService:
    def __init__(
        self,
        log_source_service: LogSourceService,
        llm_service: LLMService,
        notification_service: NotificationService,
        app_settings: AppSettings,
        formatter: ReportFormatter,
    ) -> None:
        self.log_source_service = log_source_service
        self.llm_service = llm_service
        self.notification_service = notification_service
        self.app_settings = app_settings
        self.formatter = formatter

        self._no_errors_count = 0

    async def analyze_logs(self, hours: int, msg_without_errors: bool = False) -> str:
        logger.info("Fetching recent error logs for analysis...")
        logs = await self.log_source_service.get_recent_errors(hours=hours)

        await self._check_count_of_logs_and_notify(
            logs=logs, msg_without_errors=msg_without_errors, hours=hours
        )

        self._no_errors_count = 0
        logger.info(f"Found {logs.total_count} error logs")
        grouped = await self.log_source_service._group_errors_by_type(logs)

        logger.info("Analyzing logs with LLM...")
        analysis = await self.llm_service.analyze_logs(logs)

        logger.info("Analysis completed successfully.")
        logger.info(
            f"Tokens used: {analysis.input_tokens_used} input, {analysis.output_tokens_used} output"
        )

        report_obj = self.prepare_report_from_llm(
            analysis=analysis, grouped_logs=grouped, hours=hours
        )
        report = self.formatter.to_html(data=report_obj)

        return report

    async def analyze_and_notify(self, hours: int) -> None:
        msg = await self.analyze_logs(hours=hours)
        if msg:
            message_send = await self.notification_service.send_message(message=msg)
            if not message_send:
                logger.error(f"Telegram message is not send!")

    async def get_recent_errors(self, hours: int) -> str:
        logger.info("Fetching recent error logs...")
        recent_errors = await self.log_source_service.get_recent_errors(hours=hours)

        await self._check_count_of_logs_and_notify(logs=recent_errors, hours=hours)
        self._no_errors_count = 0

        report_obj = self.prepare_report_recent_errors(recent_errors=recent_errors, hours=hours)
        report = self.formatter.to_html(data=report_obj, template_name=ReportTemplate.RECENT_LOGS)

        return report

    async def _check_count_of_logs_and_notify(
        self, logs: LogsSourceQueryResult, hours: int, msg_without_errors: bool = False
    ) -> str:
        if logs.total_count == 0:
            self._no_errors_count += 1
            msg = f"No error logs found in the {self.app_settings.schedule_interval_hours if self.app_settings.schedule_interval_hours else None} hour/s."
            logger.info(msg)
            if self._no_errors_count < 1:
                await self.notification_service.send_message(msg)
            if msg_without_errors:
                await self.notification_service.send_message(msg)

        return f"No errors found in last {hours} h."

    @retry(max_attempts=5, backoff=10.0)
    async def check_readiness(self) -> bool:
        coros = (self.log_source_service.check_readiness(),)

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
            title=f"Recent logs for the last {hours} hour/s.",
            time_range_hours=hours,
            total_errors=recent_errors.total_count,
        )
        return report_obj

    def prepare_report_from_llm(
        self, analysis: LLMAnalysisResult, grouped_logs: LogsByErrorType, hours: int
    ) -> ReportData:
        total_errors = sum(len(group.logs) for group in grouped_logs.logs_groups)
        groups = [
            ErrorGroup(error_type=group.error, count=len(group.logs))
            for group in grouped_logs.logs_groups
        ]
        report_obj = ReportData(
            title=f"Error report for the last {hours} hour/s.",
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
