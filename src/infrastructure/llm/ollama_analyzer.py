import re
from http import HTTPMethod, HTTPStatus
from logging import getLogger
from typing import Any

import msgspec
from httpx import Response

from src.application.ports.llm_analyzer import LLMAnalyzer
from src.core.exceptions import LLMError
from src.core.settings.app_settings import AppSettings
from src.domain.entities.log_entry import LogEntry
from src.infrastructure.clients.http_client import HTTPClient
from src.infrastructure.llm.providers import LLMProvider
from src.responses import LLMAnalysisResult, OllamaErrorResponse, OllamaResponse

logger = getLogger(__name__)


class OllamaAnalyzer(LLMAnalyzer):
    def __init__(self, http_client: HTTPClient, settings: AppSettings):
        self.http = http_client
        self.settings = settings

    async def analyze(self, logs: list[LogEntry]) -> LLMAnalysisResult:
        request_data = self._build_request(logs)

        response = await self.http.make_request(
            url=f"{self.settings.llm_provider.ollama.base_url}/api/chat",
            method=HTTPMethod.POST,
            data=request_data,
            timeout=self.settings.llm_provider.ollama.timeout,
            no_log_answer=True,
        )

        return self._parse_response(response_bytes=response.content)

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

    def _build_request(self, logs: list[LogEntry]) -> dict[str, Any]:
        logs_text = self._format_logs_for_llm(logs)
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
