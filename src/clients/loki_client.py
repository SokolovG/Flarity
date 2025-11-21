from datetime import datetime
from http import HTTPMethod, HTTPStatus
from logging import getLogger

import msgspec

from src.clients.base_client import BaseClient
from src.core.settings import settings
from src.entities.enums import Directions, LogLevel
from src.entities.loki import LogEntry
from src.responses.loki_responses import LokiQueryRangeResponse, LokiQueryResult

logger = getLogger(__name__)


class LokiClient(BaseClient):
    URL = settings.LOKI_URL

    async def query_range(
        self,
        query: str,
        start_time: datetime,
        end_time: datetime,
        limit: int = 1000,
        direction: Directions = Directions.BACKWARD,
    ) -> LokiQueryResult:
        logger.debug("Getting logs from loki...")

        params = {
            "query": query,
            "start": str(int(start_time.timestamp() * 1_000_000_000)),
            "end": str(int(end_time.timestamp() * 1_000_000_000)),
            "limit": str(limit),
            "direction": direction.value,
        }

        response = await self._http.make_request(
            method=HTTPMethod.GET,
            url=f"{self.URL}/loki/api/v1/query_range",
            params=params,
        )

        if response.status_code != 200:
            logger.error(f"Loki returned {response.status_code}: {response.text}")
            return LokiQueryResult(logs=[], total_count=0)

        loki_resp = msgspec.json.decode(response.content, type=LokiQueryRangeResponse)
        logs = []
        # TODO: накидал предварительно чтобы саму идею не забыть(хочу работать с сущностями)- скорее всего пиздец неэфекктивно, фикс
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
        logger.debug(f"Logs - {logs}")
        result = LokiQueryResult(logs=logs, total_count=len(logs))
        return result

    async def is_loki_is_ready(self) -> bool:
        logger.debug("Calling for loki client!")
        try:
            response = await self._http.make_request(
                url=f"{self.URL}/ready", method=HTTPMethod.GET, timeout=5, no_log_answer=True
            )
            logger.debug(f"Status code - {response.status_code}")
            return bool(response.status_code == HTTPStatus.OK)
        except Exception:
            return False
