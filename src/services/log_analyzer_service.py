from logging import getLogger

from src.services.loki_service import LokiService

logger = getLogger(__name__)


class LogAnalysisService:
    def __init__(self, loki_service: LokiService) -> None:
        self.loki_service = loki_service

    async def analyze_and_notify(self) -> None:
        logger.debug("Calling for loki service")
        logs = await self.loki_service.get_recent_errors()

        # ANALYZE

    async def check_readiness(self) -> bool:
        success_services: list[bool] = []
        loki_is_ready = await self.loki_service.check_if_loki_is_ready()
        # other services
        success_services.append(loki_is_ready)

        if False in success_services:
            return False
        return True

    async def prepare_report(self) -> None: ...
