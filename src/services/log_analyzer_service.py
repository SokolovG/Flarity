import asyncio
from logging import getLogger

from src.core.decorators import retry
from src.exceptions import ServiceNotReadyError
from src.services import LLMService, LokiService, NotificationService

logger = getLogger(__name__)


class LogAnalysisService:
    def __init__(
        self,
        loki_service: LokiService,
        llm_service: LLMService,
        notification_service: NotificationService,
    ) -> None:
        self.loki_service = loki_service
        self.llm_service = llm_service
        self.notification_service = notification_service

    async def analyze_and_notify(self) -> None:
        logger.info("Fetching recent error logs...")
        logs = await self.loki_service.get_recent_errors()

        if logs.total_count == 0:
            logger.warning("No error logs found in the last hour")
            return

        logger.info(f"Found {logs.total_count} error logs")
        logger.info("Grouping errors by type...")
        grouped = await self.loki_service.group_errors_by_type(logs)

        for group in grouped.logs_groups:
            logger.info(f"  - {group.error}: {len(group.logs)} occurrences")

        logger.info("Analyzing logs with LLM...")
        analysis = await self.llm_service.analyze_logs(logs)

        logger.info("Analysis complete!")
        logger.info(f"Analysis result:\n{analysis.analysis_text}")
        logger.info(
            f"Tokens used: {analysis.input_tokens_used} input, {analysis.output_tokens_used} output"
        )

        message_send = await self.notification_service.send_analysis_report(
            analysis=analysis, grouped_logs=grouped
        )
        logger.info(f"Telegram message has sent is {message_send}")

    @retry(max_attempts=5, backoff=10.0, retryable_exceptions=(ServiceNotReadyError,))
    async def check_readiness(self) -> bool:
        coros = (
            self.loki_service.check_if_loki_is_ready(),
            self.llm_service.check_if_llm_is_ready(),
        )

        loki_ready, llm_ready = await asyncio.gather(*coros, return_exceptions=True)
        services = {
            "Loki": loki_ready,
            "LLM": llm_ready,
        }

        not_ready = []
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

    async def prepare_report(self) -> None: ...
