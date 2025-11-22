from logging import getLogger
from typing import Final

from src.clients.base_client import BaseClient
from src.core.settings import settings
from src.entities.enums import LLMProvider
from src.responses import LLMResponse, LokiQueryResult

logger = getLogger(__name__)


class LLMClient(BaseClient):
    URL: Final[str] = settings.LOCAL_LLM_URL
    PROVIDER: Final[LLMProvider] = settings.LLMProvider

    async def is_llm_is_ready(self) -> bool:
        logger.debug("Calling for llm to check if she is ready!")
        return True

    async def send_request_to_llm(self, logs: LokiQueryResult) -> LLMResponse: ...  # type: ignore
