from application.ports.log_repository import LogRepository
from infrastructure.clients.loki_client import LokiClient
from src.domain.entities.log_entry import LogEntry
from src.domain.value_objects.time_range import TimeRange
from src.responses.logs_base_responses import LogsSourceQueryResult


class LokiLogRepository(LogRepository):
    def __init__(self, loki_client: LokiClient):
        self.client = loki_client

    async def get_errors(self, time_range: TimeRange) -> list[LogEntry]:
        query = f'{{level="error"}}'
        start, end = time_range.to_timestamps()

        response = await self.client.query_range(query, start, end)

        return self._parse_logs(response)

    def _parse_logs(self, response: LogsSourceQueryResult) -> list[LogEntry]:
        """Loki response → LogEntry"""
