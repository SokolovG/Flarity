import json
from datetime import datetime
from http import HTTPMethod, HTTPStatus
from logging import getLogger

import msgspec

from src.domain.entities.enums import Directions
from src.infrastructure.clients.http_client import HTTPClient
from src.infrastructure.exceptions import LokiError, LokiUnavailableError
from src.infrastructure.responses.loki_responses import LokiQueryRangeResponse
from src.infrastructure.settings.log_source_settings import LogsSourceSettings

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
    ) -> LokiQueryRangeResponse:
        params = {
            "query": query,
            "start": str(int(start_time.timestamp() * 1_000_000_000)),
            "end": str(int(end_time.timestamp() * 1_000_000_000)),
            "limit": str(limit),
            "direction": direction.value,
        }

        http_response = await self._http.make_request(
            method=HTTPMethod.GET,
            url=f"{self.settings.get_config.url}/loki/api/v1/query_range",  # type: ignore [attr-defined]
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

    async def is_loki_is_ready(self) -> bool:
        try:
            response = await self._http.make_request(
                url=f"{self.settings.get_config.url}/ready",  # type: ignore [attr-defined]
                method=HTTPMethod.GET,
                timeout=5,
                no_log_answer=True,
            )
            return bool(response.status_code == HTTPStatus.OK)
        except Exception:
            return False
