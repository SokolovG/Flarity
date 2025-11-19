from datetime import datetime
from http import HTTPMethod, HTTPStatus
from src.clients.base_client import BaseClient
from src.core.settings import settings
from src.entities.enums import Directions
from src.responses.loki_responses import LokiLogsResponse


class LokiClient(BaseClient):
    URL = settings.LOKI_URL

    async def query_range(
        self,
        query: str,
        start_time: datetime,
        end_time: datetime,
        limit: int = 1000,
        direction: Directions = Directions.BACKWARD,
    ) -> LokiLogsResponse:
        return LokiLogsResponse()

    async def get_recent_errors(self, hours: int = 1) -> LokiLogsResponse:
        return LokiLogsResponse()

    async def is_loki_is_ready(self) -> bool:
        try:
            response = await self._http.make_request(
                url=f"{self.URL}/ready", method=HTTPMethod.GET, timeout=5
            )
            return bool(response.status_code == HTTPStatus.OK)
        except Exception:
            return False
