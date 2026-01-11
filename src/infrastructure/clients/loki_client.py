from datetime import datetime
from http import HTTPMethod, HTTPStatus
from logging import getLogger
from typing import Final

import msgspec

from src.domain.entities.enums import Directions
from src.infrastructure.clients.http_client import HTTPClient
from src.infrastructure.exceptions import LokiError, LokiUnavailableError
from src.infrastructure.repositories.loki.responses import LokiQueryRangeResponse
from src.infrastructure.settings.providers import LogsSourceSettings, LokiConfig

logger = getLogger(__name__)

NANOS_PER_SECOND: Final[int] = 1_000_000_000


class LokiClient:
    def __init__(self, http_client: HTTPClient, settings: LogsSourceSettings):
        self._http = http_client
        self.config = settings.get_config(LokiConfig)
        self.url = self.config.url

    async def query_range(
        self,
        query: str,
        start_time: datetime,
        end_time: datetime,
        limit: int = 1000,
        direction: Directions = Directions.BACKWARD,
    ) -> LokiQueryRangeResponse:
        params = {
            "query": query,
            "start": self._to_loki_timestamp(start_time),
            "end": self._to_loki_timestamp(end_time),
            "limit": str(limit),
            "direction": direction.value,
        }

        http_response = await self._http.make_request(
            method=HTTPMethod.GET,
            url=f"{self.url}/loki/api/v1/query_range",
            params=params,
            timeout=10,
            no_log_answer=True,
        )

        if http_response.status_code == HTTPStatus.SERVICE_UNAVAILABLE:
            raise LokiUnavailableError("Loki is temporarily unavailable")
        elif http_response.status_code >= HTTPStatus.INTERNAL_SERVER_ERROR:
            raise LokiError(f"Loki server error: {http_response.status_code}")
        elif http_response.status_code >= HTTPStatus.BAD_REQUEST:
            raise LokiError(f"Bad request: {http_response.status_code}")

        response = msgspec.json.decode(http_response.content, type=LokiQueryRangeResponse)
        return response

    def _to_loki_timestamp(self, dt: datetime) -> str:
        return str(int(dt.timestamp() * NANOS_PER_SECOND))

    async def check_loki_readiness(self) -> bool:
        try:
            response = await self._http.make_request(
                url=f"{self.url}/ready",
                method=HTTPMethod.GET,
                timeout=5,
                no_log_answer=True,
            )
            return bool(response.status_code == HTTPStatus.OK)
        except Exception:
            return False
