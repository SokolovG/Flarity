from logging import getLogger
from typing import Final

from src.clients.base_client import BaseClient
from src.core.decorators import retry
from src.core.settings import Settings
from src.entities.enums import LLMProvider
from src.responses import LLMResponse, LokiQueryResult

logger = getLogger(__name__)


class LLMClient(BaseClient):
    async def is_llm_is_ready(self) -> bool:
        return True

    @retry(max_attempts=5, backoff=10)
    async def send_request_to_llm(self, logs: LokiQueryResult) -> LLMResponse: ...  # type: ignore
