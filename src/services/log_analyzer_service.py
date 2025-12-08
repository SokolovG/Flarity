import asyncio
from logging import getLogger

from src.core.decorators import retry
from src.core.settings.app_settings import AppSettings
from src.entities.report import ReportData
from src.exceptions import ServiceNotReadyError
from src.responses.llm_base_responses import LLMAnalysisResult
from src.responses.logs_base_responses import LogsByErrorType
from src.services import LLMService, LogSourceService
from src.services.notification_service import NotificationService

logger = getLogger(__name__)


class LogAnalysisService:
    def __init__(
        self,
        log_source_service: LogSourceService,
        llm_service: LLMService,
        notification_service: NotificationService,
        app_settings: AppSettings,
    ) -> None:
        self.log_source_service = log_source_service
        self.llm_service = llm_service
        self.notification_service = notification_service
        self.app_settings = app_settings

    async def analyze_and_notify(self) -> None:
        logger.info("Fetching recent error logs...")
        logs = await self.log_source_service.get_recent_errors(
            hours=int(self.app_settings.schedule_interval_hours)
        )

        if logs.total_count == 0:
            logger.warning("No error logs found in the last hour")
            return

        logger.info(f"Found {logs.total_count} error logs")
        logger.info("Grouping errors by type...")
        grouped = await self.log_source_service._group_errors_by_type(logs)

        for group in grouped.logs_groups:
            logger.info(f"  - {group.error}: {len(group.logs)} occurrences")

        logger.info("Analyzing logs with LLM...")
        analysis = await self.llm_service.analyze_logs(logs)

        logger.info("Analysis complete!")
        logger.info(
            f"Tokens used: {analysis.input_tokens_used} input, {analysis.output_tokens_used} output"
        )

        report_obj = self.prepare_report(analysis=analysis, grouped_logs=grouped)
        message_send = await self.notification_service.send_analysis_report(report_data=report_obj)
        logger.info(f"Telegram message has sent is {message_send}")

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

    def prepare_report(
        self, analysis: LLMAnalysisResult, grouped_logs: LogsByErrorType
    ) -> ReportData:
        total_errors = sum(len(group.logs) for group in grouped_logs.logs_groups)
        report_obj = ReportData(
            title="<b>Отчет по ошибкам за последний час</b>\n",
            time_range_hours=int(self.app_settings.schedule_interval_hours),
            total_errors=total_errors,
            unique_types=len(grouped_logs.logs_groups),
            ai_analysis=analysis.analysis_text,
            provider=analysis.provider.value,
            tokens_in=analysis.input_tokens_used,
            tokens_out=analysis.output_tokens_used,
        )
        return report_obj
