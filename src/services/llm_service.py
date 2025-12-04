from logging import getLogger

from src.exceptions.llm_exceptions import LLMError
from src.llm_adapters import BaseLLMAdapter
from src.responses import LLMAnalysisResult, LogsSourceQueryResult

logger = getLogger(__name__)


class LLMService:
    def __init__(self, adapter: BaseLLMAdapter) -> None:
        self.adapter = adapter

    async def analyze_logs(self, logs: LogsSourceQueryResult) -> LLMAnalysisResult:
        if not logs:
            raise ValueError("No logs to analyze")

        result = await self.adapter.analyze_logs(logs.logs)
        return result
