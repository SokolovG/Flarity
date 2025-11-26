from logging import getLogger

from src.exceptions.llm_exceptions import LLMError
from src.llm_adapters import BaseLLMAdapter
from src.responses import LLMAnalysisResult, LokiQueryResult

logger = getLogger(__name__)


class LLMService:
    def __init__(self, adapter: BaseLLMAdapter) -> None:
        self.adapter = adapter

    async def check_if_llm_is_ready(self) -> bool:
        try:
            # TODO: Простой health check
            return True
        except LLMError:
            return False

    async def analyze_logs(self, logs: LokiQueryResult) -> LLMAnalysisResult:
        if not logs:
            raise ValueError("No logs to analyze")

        result = await self.adapter.analyze_logs(logs.logs)
        return result
