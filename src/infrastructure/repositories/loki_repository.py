import json
from datetime import datetime, timezone
from logging import getLogger

from src.application.ports.log_source import LogSource
from src.domain.entities.enums import LogLevel
from src.domain.entities.log_entry import LogEntry
from src.domain.value_objects.time_range import TimeRange
from src.infrastructure.clients.loki_client import LokiClient
from src.infrastructure.decorators import log_calls
from src.infrastructure.responses.loki_responses import LokiQueryRangeResponse

logger = getLogger(__name__)


class LokiLogRepository(LogSource):
    def __init__(self, loki_client: LokiClient):
        self.client = loki_client

    @log_calls
    async def get_errors(self, time_range: TimeRange) -> list[LogEntry]:
        """
        Fetch error logs from Loki.

        NOTE: Limited to 1000 most recent errors per query.
        For high-volume periods, some errors may be skipped.
        """
        app_name = self.client.config.app_name
        query = f'{{level="error", app="{app_name}"}}'
        start, end = time_range.to_timestamps(datetime.now(timezone.utc))

        raw_response = await self.client.query_range(query, start, end)

        return self._map_to_domain(raw_response)

    def _map_to_domain(self, response: LokiQueryRangeResponse) -> list[LogEntry]:
        logs = []
        for stream in response.data.result:
            for timestamp_ns, message in stream.values:
                parsed = self._parse_log_message(message)
                actual_message = parsed.get("message", message)
                logs.append(
                    LogEntry(
                        timestamp=datetime.fromtimestamp(int(timestamp_ns) / 1e9),
                        message=actual_message,
                        level=LogLevel.ERROR,
                        app=stream.stream.get("app", "unknown"),
                        metadata={
                            "target": parsed.get("target") or "",
                            "request_id": parsed.get("request_id") or "",
                            "method": parsed.get("method") or "",
                            "uri": parsed.get("uri") or "",
                        },
                    )
                )
        return logs

    def _parse_log_message(self, message: str) -> dict:
        try:
            _dict: dict = json.loads(message)
            return _dict
        except json.JSONDecodeError:
            logger.warning(f"Failed to parse log as JSON: {message[:100]}")
            return {}

    async def check_readiness(self) -> bool:
        return await self.client.is_loki_is_ready()
