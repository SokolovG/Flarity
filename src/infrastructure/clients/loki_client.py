import json
from datetime import datetime
from http import HTTPMethod, HTTPStatus
from logging import getLogger

import msgspec

from src.core.settings.log_source_settings import LogsSourceSettings
from src.domain.entities.enums import Directions, LogLevel
from src.domain.entities.log_entry import LogEntry
from src.exceptions import LokiError, LokiUnavailableError
from src.infrastructure.clients.http_client import HTTPClient
from src.responses import (
    LogsSourceQueryResult,
    LokiQueryRangeResponse,
)

logger = getLogger(__name__)


class LokiClient:
    def __init__(self, http_client: HTTPClient, settings: LogsSourceSettings):
        self._http = http_client
        self.settings = settings

    async def query_range(
        self,
        query: str,
        start_time: datetime,
        end_time: datetime,
        limit: int = 1000,
        direction: Directions = Directions.BACKWARD,
    ) -> LogsSourceQueryResult:
        params = {
            "query": query,
            "start": str(int(start_time.timestamp() * 1_000_000_000)),
            "end": str(int(end_time.timestamp() * 1_000_000_000)),
            "limit": str(limit),
            "direction": direction.value,
        }

        response = await self._http.make_request(
            method=HTTPMethod.GET,
            url=f"{self.settings.loki_url}/loki/api/v1/query_range",
            params=params,
            no_log_answer=True,
        )

        if response.status_code == HTTPStatus.SERVICE_UNAVAILABLE:
            raise LokiUnavailableError("Loki is temporarily unavailable")
        elif response.status_code >= HTTPStatus.INTERNAL_SERVER_ERROR:
            raise LokiError(f"Loki server error: {response.status_code}")
        elif response.status_code >= HTTPStatus.BAD_REQUEST:
            raise LokiError(f"Bad request: {response.status_code}")

        loki_resp = msgspec.json.decode(response.content, type=LokiQueryRangeResponse)
        logs = []
        for stream in loki_resp.data.result:
            for timestamp_ns, message in stream.values:
                parsed = self._parse_log_message(message)

                logs.append(
                    LogEntry(
                        timestamp=datetime.fromtimestamp(int(timestamp_ns) / 1e9),
                        message=parsed.get("message", message),
                        level=LogLevel.ERROR,
                        app=stream.stream.get("app", "unknown"),
                        target=parsed.get("target"),
                        request_id=parsed.get("span", {}).get("request_id"),
                        method=parsed.get("span", {}).get("method"),
                        uri=parsed.get("span", {}).get("uri"),
                    )
                )
        result = LogsSourceQueryResult(logs=logs, total_count=len(logs))
        return result

    def _parse_log_message(self, message: str) -> dict:
        try:
            _dict: dict = json.loads(message)
            return _dict
        except json.JSONDecodeError:
            logger.warning(f"Failed to parse log as JSON: {message[:100]}")
            return {}

    async def is_loki_is_ready(self) -> bool:
        try:
            response = await self._http.make_request(
                url=f"{self.settings.loki_url}/ready",
                method=HTTPMethod.GET,
                timeout=5,
                no_log_answer=True,
            )
            return bool(response.status_code == HTTPStatus.OK)
        except Exception:
            return False
