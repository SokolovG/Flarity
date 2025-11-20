from src.clients.loki_client import LokiClient
from src.core.settings import Settings
from src.entities.enums import LogLevel
from src.responses.loki_responses import LokiQueryResult


class LokiService:
    def __init__(self, loki_client: LokiClient) -> None:
        self.loki_client = loki_client
        self.app_name = Settings.LOKI_APP_NAME

    async def get_recent_errors(self, hours: int = 1) -> LokiQueryResult:
        """Получает только ERROR логи за N часов"""
        return await self.get_logs_by_level(LogLevel.ERROR, hours)

    async def get_logs_by_level(self, level: LogLevel, hours: int = 1) -> LokiQueryResult:
        return LokiQueryResult()
