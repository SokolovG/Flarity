from http import HTTPMethod, HTTPStatus
from logging import getLogger

import msgspec

from src.core.decorators import retry
from src.entities.enums import LLMProvider
from src.entities.loki import LogEntry
from src.exceptions.llm_exceptions import LLMError
from src.llm_adapters.base_adapter import BaseLLMAdapter
from src.responses import LLMAnalysisResult, OllamaErrorResponse, OllamaResponse

logger = getLogger(__name__)


class OllamaAdapter(BaseLLMAdapter):
    @retry(max_attempts=5, backoff=10, retryable_exceptions=(LLMError,))
    async def analyze_logs(self, logs: list[LogEntry]) -> LLMAnalysisResult:
        logs_text = self.format_logs_for_llm(logs=logs)
        full_text = self.settings.get_system_prompt + logs_text
        request_data: dict = {"model": self.settings.LLMModel.value, "prompt": full_text}

        response = await self.http.make_request(
            url=f"{self.settings.OLLAMA_BASE_URL}/api/generate",
            method=HTTPMethod.POST,
            data=request_data,
            timeout=self.settings.OLLAMA_TIMEOUT,
        )

        if response.status_code == HTTPStatus.NOT_FOUND:
            raise LLMError(
                "Ollama model not found. Did you run 'ollama pull'?",
                details={"status": response.status_code, "model": self.settings.OLLAMA_MODEL},
            )

        if response.status_code >= 500:
            raise LLMError(
                f"Ollama server error: {response.status_code}",
                details={"status": response.status_code, "response": response.text},
            )

        if response.status_code != 200:
            raise LLMError(
                f"Ollama API error: {response.status_code}",
                details={"status": response.status_code, "response": response.text},
            )

        return self._parse_response(response_bytes=response.content)

    def _parse_response(self, response_bytes: bytes) -> LLMAnalysisResult:
        try:
            response_model = msgspec.json.decode(response_bytes, type=OllamaResponse)
        except msgspec.DecodeError:
            try:
                error = msgspec.json.decode(response_bytes, type=OllamaErrorResponse)
                raise LLMError(f"Ollama error: {error.error}")
            except msgspec.DecodeError:
                raise LLMError(f"Failed to parse Ollama response: {response_bytes.decode()[:200]}")

        text = response_model.response

        if not text or len(text.strip()) < 10:
            raise LLMError("LLM returned empty or too short response")

        if not text.rstrip().endswith((".", "!", "?")):
            logger.warning("LLM response might be truncated")

        return LLMAnalysisResult(
            analysis_text=text,
            provider=LLMProvider.OLLAMA,
            input_tokens_used=response_model.prompt_eval_count,
            output_tokens_used=response_model.eval_count,
        )
