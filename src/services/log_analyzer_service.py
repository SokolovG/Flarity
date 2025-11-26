import asyncio
from logging import getLogger

from src.core.decorators import retry
from src.exceptions import ServiceNotReadyError
from src.services.llm_service import LLMService
from src.services.loki_service import LokiService

logger = getLogger(__name__)


class LogAnalysisService:
    def __init__(self, loki_service: LokiService, llm_service: LLMService) -> None:
        self.loki_service = loki_service
        self.llm_service = llm_service

    async def analyze_and_notify(self) -> None:
        logs = await self.loki_service.get_recent_errors()

        # ANALYZE

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
