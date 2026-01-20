import re
from http import HTTPStatus
from logging import getLogger
from typing import Any

import msgspec
from httpx import Response

from src.application.dto.analysis_result import LLMAnalysisResult
from src.domain.entities.enums import LLMModel, LLMProvider
from src.infrastructure.clients.http_client import HTTPClient
from src.infrastructure.exceptions import LLMAuthError, LLMError, LLMRateLimitError
from src.infrastructure.llm.base_http_llm_analyzer import BaseLLMAnalyzer
from src.infrastructure.llm.dto.session import LLMMessage
from src.infrastructure.llm.yandex.responses import YandexResponse
from src.infrastructure.settings.app_settings import AppSettings
from src.infrastructure.settings.providers import YandexConfig

logger = getLogger(__name__)


class YandexAnalyzer(BaseLLMAnalyzer):
    def __init__(self, http_client: HTTPClient, settings: AppSettings) -> None:
        super().__init__(http_client, settings)

    def _get_api_url(self) -> str:
        url = self.settings.llm_provider.get_config(YandexConfig).base_url
        return url

    def _get_headers(self) -> dict[str, Any]:
        headers = {
            "Authorization": f"Api-Key {self.settings.llm_provider.get_config(YandexConfig).api_key}",
            "Content-Type": "application/json",
        }
        return headers

    def _build_request_from_context(self, context: list[LLMMessage]) -> dict[str, Any]:
        request_data = {
            "modelUri": self._get_model_uri(),
            "completionOptions": {
                "stream": False,
                "temperature": self.settings.llm_settings.temperature,
                "maxTokens": self.settings.llm_settings.max_tokens,
            },
            "messages": msgspec.to_builtins(context),
        }
        return request_data

    def _build_request(self, logs_text: str) -> tuple[dict[str, Any], list[LLMMessage]]:
        messages = [
            LLMMessage(role="system", text=self.settings.llm_settings.system_prompt),
            LLMMessage(role="user", text=logs_text),
        ]
        request_data = {
            "modelUri": self._get_model_uri(),
            "completionOptions": {
                "stream": False,
                "temperature": self.settings.llm_settings.temperature,
                "maxTokens": self.settings.llm_settings.max_tokens,
            },
            "messages": msgspec.to_builtins(messages),
        }
        return request_data, messages

    def _handle_response(self, response: Response) -> None:
        if response.status_code in (HTTPStatus.UNAUTHORIZED, HTTPStatus.FORBIDDEN):
            raise LLMAuthError("Authorization failed!", details={"status": response.status_code})
        elif response.status_code == HTTPStatus.TOO_MANY_REQUESTS:
            raise LLMRateLimitError("Rate limit exceeded", details={"status": response.status_code})
        if response.status_code >= 500:
            raise LLMError(
                f"Yandex server error: {response.status_code}",
                details={"status": response.status_code, "response": response.text},
            )
        if response.status_code != 200:
            raise LLMError(
                f"Yandex API error: {response.status_code}",
                details={"status": response.status_code, "response": response.text},
            )

    def _parse_response(
        self, response_bytes: bytes, messages: list[LLMMessage]
    ) -> LLMAnalysisResult:
        try:
            response_model = msgspec.json.decode(response_bytes, type=YandexResponse)
        except msgspec.DecodeError as e:
            raise LLMError(f"Error during llm generation {e}")

        text = response_model.result.alternatives[0].message.text
        text = self._clean_llm_answer(text)

        if not text or len(text.strip()) < 10:
            raise LLMError("LLM returned empty or too short response")

        input_used_token = response_model.result.usage.inputTextTokens
        output_used_token = response_model.result.usage.completionTokens

        return LLMAnalysisResult(
            messages=messages,
            analysis_text=text,
            provider=LLMProvider.YANDEX,
            input_tokens_used=int(input_used_token),
            output_tokens_used=int(output_used_token),
        )

    def _get_model_uri(self) -> str:
        modelUri = f"gpt://{self.settings.llm_provider.get_config(YandexConfig).catalog_id}/{self.settings.llm_settings.model.value}"
        match self.settings.llm_settings.model:
            case LLMModel.YANDEX_GPT_5:
                modelUri += "latest"
        return modelUri

    @staticmethod
    def _clean_llm_answer(text: str) -> str:
        text = re.sub(r"<think>.*?</think>", "", text, flags=re.DOTALL)
        text = re.sub(r"^#+\s", "", text, flags=re.MULTILINE)
        text = re.sub(r"\*\*(.+?)\*\*", r"\1", text)
        return text.strip()
