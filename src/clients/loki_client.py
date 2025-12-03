from datetime import datetime
from http import HTTPMethod, HTTPStatus
from logging import getLogger

import msgspec

from src.clients import HTTPClient
from src.core.decorators import retry
from src.core.settings.log_source_settings import LogsSourceSettings
from src.entities.enums import Directions, LogLevel
from src.entities.loki import LogEntry
from src.exceptions import LokiError, LokiUnavailableError
from src.responses import (
    LogsSourceQueryResult,
    LokiQueryRangeResponse,
)

logger = getLogger(__name__)


class LokiClient:
    def __init__(self, http_client: HTTPClient, settings: LogsSourceSettings):
        self._http = http_client
        self.settings = settings

    @retry(max_attempts=3, backoff=2.0)
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

        if response.status_code == 503:
            raise LokiUnavailableError("Loki is temporarily unavailable")
        elif response.status_code >= 500:
            raise LokiError(f"Loki server error: {response.status_code}")
        elif response.status_code >= 400:
            raise LokiError(f"Bad request: {response.status_code}")

        loki_resp = msgspec.json.decode(response.content, type=LokiQueryRangeResponse)
        logs = []
        # TODO: накидал предварительно чтобы саму идею не забыть(хочу работать с сущностями)- скорее всего пиздец неэфекктивно, фикс
        # также вынести лучше в сервис бизнес логику
        for stream in loki_resp.data.result:
            for timestamp_ns, message in stream.values:
                level_str = stream.stream.get("level", "error")
                try:
                    level = LogLevel(level_str)
                except ValueError:
                    level = LogLevel.ERROR  # fallback
                    logger.warning(f"Unknown log level: {level_str}")

                logs.append(
                    LogEntry(
                        timestamp=datetime.fromtimestamp(int(timestamp_ns) / 1e9),
                        message=message,
                        level=level,
                        app=stream.stream.get("app", "unknown"),
                    )
                )
        result = LogsSourceQueryResult(logs=logs, total_count=len(logs))
        return result

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
