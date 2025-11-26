from logging import getLogger

from src.llm_adapters import BaseLLMAdapter
from src.responses import LLMAnalysisResult, LokiQueryResult

logger = getLogger(__name__)


class LLMService:
    def __init__(self, adapter: BaseLLMAdapter) -> None:
        self.adapter = adapter

    async def check_if_llm_is_ready(self) -> bool:
        return True

    async def anylize_logs(self, logs: LokiQueryResult) -> LLMAnalysisResult:
        #
        return await self.adapter.analyze_logs(logs)
