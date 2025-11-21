from logging import getLogger

from src.clients.llm_client import LLMClient
from src.responses import LLMResponse, LokiQueryResult

logger = getLogger(__name__)


class LLMService:
    def __init__(self, llm_client: LLMClient) -> None:
        self.llm_client = llm_client

    async def check_if_llm_is_ready(self) -> bool:
        logger.debug("Calling for llm client to check if he is ready")
        ready = await self.llm_client.is_llm_is_ready()
        return ready

    async def anylize_logs(self, logs: LokiQueryResult) -> LLMResponse: ...  # type: ignore
