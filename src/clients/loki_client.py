from datetime import datetime
from http import HTTPMethod, HTTPStatus
from logging import getLogger

import msgspec

from src.clients.base_client import BaseClient
from src.core.decorators import retry
from src.core.settings import Settings
from src.entities.enums import Directions, LogLevel
from src.entities.loki import LogEntry
from src.exceptions import LokiError, LokiUnavailableError
from src.responses.loki_responses import LokiQueryRangeResponse, LokiQueryResult

logger = getLogger(__name__)


class LokiClient(BaseClient):
    @retry(max_attempts=3, backoff=2.0, retryable_exceptions=(LokiUnavailableError,))
    async def query_range(
        self,
        query: str,
        start_time: datetime,
        end_time: datetime,
        limit: int = 1000,
        direction: Directions = Directions.BACKWARD,
    ) -> LokiQueryResult:
        params = {
            "query": query,
            "start": str(int(start_time.timestamp() * 1_000_000_000)),
            "end": str(int(end_time.timestamp() * 1_000_000_000)),
            "limit": str(limit),
            "direction": direction.value,
        }

        response = await self._http.make_request(
            method=HTTPMethod.GET,
            url=f"{self.settings.LOKI_URL}/loki/api/v1/query_range",
            params=params,
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
        logger.info(f"Logs from loki: {logs}")
        result = LokiQueryResult(logs=logs, total_count=len(logs))
        return result

    async def is_loki_is_ready(self) -> bool:
        try:
            response = await self._http.make_request(
                url=f"{self.settings.LOKI_URL}/ready", method=HTTPMethod.GET, timeout=5
            )
            return bool(response.status_code == HTTPStatus.OK)
        except Exception:
            return False
