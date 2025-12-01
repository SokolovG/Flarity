from logging import getLogger

from src.core.decorators import retry
from src.entities.loki import LogEntry
from src.exceptions.llm_exceptions import LLMError, LLMRateLimitError
from src.llm_adapters.base_adapter import BaseLLMAdapter
from src.responses import LLMAnalysisResult

logger = getLogger(__name__)


class OllamaAdapter(BaseLLMAdapter):
    @retry(max_attempts=5, backoff=10, retryable_exceptions=(LLMError, LLMRateLimitError))
    async def analyze_logs(self, logs: list[LogEntry]) -> LLMAnalysisResult:
        request_data: dict = {}
        response = await self.http.make_request()
        return self._parse_response(response_bytes=response.content)

    def _parse_response(self, response_bytes: bytes) -> LLMAnalysisResult: ...  # type: ignore
