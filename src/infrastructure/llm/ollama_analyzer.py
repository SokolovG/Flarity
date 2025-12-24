import re
from http import HTTPStatus
from logging import getLogger
from typing import Any

import msgspec
from httpx import Response

from src.core.exceptions import LLMError
from src.domain.entities.log_entry import LogEntry
from src.infrastructure.llm.base_http_llm_analyzer import BaseHTTPLLMAnalyzer
from src.infrastructure.llm.providers import LLMProvider
from src.responses import LLMAnalysisResult, OllamaErrorResponse, OllamaResponse

logger = getLogger(__name__)


class OllamaAnalyzer(BaseHTTPLLMAnalyzer):
    def _handle_response(self, response: Response) -> None:
        if response.status_code == HTTPStatus.NOT_FOUND:
            raise LLMError(
                "Ollama model not found. Did you run 'ollama pull'?",
                details={"status": response.status_code, "model": self.settings.llm.model},
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

    def _build_request(self, logs_text: str) -> dict[str, Any]:
        request_data = {
            "model": self.settings.llm.model,
            "messages": [
                {"role": "system", "content": self.settings.llm.system_prompt},
                {"role": "user", "content": logs_text},
            ],
            "stream": False,
            "options": {"num_predict": self.settings.llm.max_tokens},
        }
        return request_data

    def _parse_response(self, response_bytes: bytes) -> LLMAnalysisResult:
        try:
            response_model = msgspec.json.decode(response_bytes, type=OllamaResponse)
        except msgspec.DecodeError:
            try:
                error = msgspec.json.decode(response_bytes, type=OllamaErrorResponse)
                raise LLMError(f"Ollama error: {error.error}")
            except msgspec.DecodeError:
                raise LLMError(f"Failed to parse Ollama response: {response_bytes.decode()[:200]}")

        text = response_model.message.content
        text = self._clean_llm_answer(text)

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

    def _get_headers(self) -> dict[str, Any]:
        return {}

    def _get_api_url(self) -> str:
        url = f"{self.settings.llm_provider.ollama.base_url}/api/chat"
        return url

    @staticmethod
    def _clean_llm_answer(text: str) -> str:
        text = re.sub(r"<think>.*?</think>", "", text, flags=re.DOTALL)
        text = text.replace("<think>", "").replace("</think>", "")
        return text.strip()

    def _format_logs_for_llm(self, logs: list[LogEntry]) -> str:
        logs_text = ""
        for log in logs:
            clean_message = log.message.encode().decode("unicode_escape")
            logs_text += f"[{log.timestamp.strftime('%Y-%m-%d %H:%M:%S')}] {log.level.value} {log.app} {clean_message}\n"

        return logs_text
