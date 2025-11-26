from src.core.decorators import retry
from src.entities.loki import LogEntry
from src.llm_adapters.base_adapter import BaseLLMAdapter
from src.responses import LLMAnalysisResult


class LocalAdapter(BaseLLMAdapter):
    @retry(max_attempts=5, backoff=10)
    async def anylize_logs(self, logs: list[LogEntry]) -> LLMAnalysisResult: ...  # type: ignore
