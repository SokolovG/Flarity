import html
import re
from http import HTTPStatus
from logging import getLogger
from typing import Any

import msgspec
from httpx import Response

from src.application.dto.analysis_result import LLMAnalysisResult
from src.domain.entities.enums import LLMProvider
from src.infrastructure.dto import LLMMessage
from src.infrastructure.exceptions import LLMError
from src.infrastructure.llm.base_http_llm_analyzer import BaseLLMAnalyzer
from src.infrastructure.llm.ollama.responses import OllamaErrorResponse, OllamaResponse
from src.infrastructure.settings.llm_provider_settings import OllamaConfig

logger = getLogger(__name__)


class OllamaAnalyzer(BaseLLMAnalyzer):
    def _handle_response(self, response: Response) -> None:
        if response.status_code == HTTPStatus.NOT_FOUND:
            raise LLMError(
                "Ollama model not found. Did you run 'ollama pull'?",
                details={"status": response.status_code, "model": self.settings.llm_settings.model},
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

    def _build_request(
        self, logs_text: str, context: list[LLMMessage] | None = None
    ) -> dict[str, Any]:
        messages = [
            LLMMessage(role="system", content=self.settings.llm_settings.system_prompt),
            LLMMessage(role="user", content=logs_text),
        ]
        if context:
            for msg in context:
                messages.append(msg)

        request_data = {
            "model": self.settings.llm_settings.model,
            "messages": msgspec.to_builtins(messages),
            "stream": False,
            "options": {"num_predict": self.settings.llm_settings.max_tokens},
        }
        return request_data

    def _build_prompt(self, logs_text: str) -> list[LLMMessage]:
        data = [
            LLMMessage(role="system", content=self.settings.llm_settings.system_prompt),
            LLMMessage(role="user", content=logs_text),
        ]
        return data

    def _parse_response(
        self, response_bytes: bytes, messages: list[LLMMessage] | None = None
    ) -> LLMAnalysisResult:
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
        # TODO: не работает в тг html
        text = self._markdown_to_html(text)

        if not text or len(text.strip()) < 10:
            raise LLMError("LLM returned empty or too short response")

        return LLMAnalysisResult(
            messages=messages,
            analysis_text=text,
            provider=LLMProvider.OLLAMA,
            input_tokens_used=response_model.prompt_eval_count,
            output_tokens_used=response_model.eval_count,
        )

    @staticmethod
    def _markdown_to_html(text: str) -> str:
        text = html.escape(text)
        # **bold** → <b>bold</b>
        text = re.sub(r"\*\*(.+?)\*\*", r"<b>\1</b>", text)
        # *italic* → <i>italic</i>
        text = re.sub(r"\*(.+?)\*", r"<i>\1</i>", text)
        # `code` → <code>code</code>
        text = re.sub(r"`(.+?)`", r"<code>\1</code>", text)
        # [link](url) → <a href="url">link</a>
        text = re.sub(r"\[(.+?)\]\((.+?)\)", r'<a href="\2">\1</a>', text)
        return text

    def _get_headers(self) -> dict[str, Any]:
        return {}

    def _get_api_url(self) -> str:
        url = f"{self.settings.llm_provider.get_config(OllamaConfig).base_url}/api/chat"
        return url

    @staticmethod
    def _clean_llm_answer(text: str) -> str:
        text = re.sub(r"<think>.*?</think>", "", text, flags=re.DOTALL)
        return text.strip()
