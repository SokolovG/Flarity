from http import HTTPStatus
from logging import getLogger
from typing import Any

import msgspec
from httpx import Response

from src.application.dto.analysis_result import LLMAnalysisResult
from src.domain.entities.enums import LLMModel, LLMProvider
from src.infrastructure.dto import LLMMessage
from src.infrastructure.exceptions import LLMAuthError, LLMError, LLMRateLimitError
from src.infrastructure.llm.base_http_llm_analyzer import BaseLLMAnalyzer
from src.infrastructure.llm.yandex.responses import YandexResponse
from src.infrastructure.settings.llm_provider_settings import YandexConfig

logger = getLogger(__name__)


class YandexAnalyzer(BaseLLMAnalyzer):
    def _get_api_url(self) -> str:
        url = self.settings.llm_provider.get_config(YandexConfig).base_url
        return url

    def _get_headers(self) -> dict[str, Any]:
        headers = {
            "Authorization": f"Api-Key {self.settings.llm_provider.get_config(YandexConfig).api_key}",
            "Content-Type": "application/json",
        }
        return headers

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
            "modelUri": self._get_model_uri(),
            "completionOptions": {
                "stream": False,
                "temperature": self.settings.llm_settings.temperature,
                "maxTokens": self.settings.llm_settings.max_tokens,
            },
            "messages": msgspec.to_builtins(messages),
        }
        return request_data

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
            response_model = msgspec.json.decode(response_bytes, type=YandexResponse)
        except msgspec.DecodeError as e:
            raise LLMError(f"Error during llm generation {e}")

        text = response_model.result.alternatives[0].message.text

        if not text or len(text.strip()) < 10:
            raise LLMError("LLM returned empty or too short response")

        if not text.rstrip().endswith((".", "!", "?")):
            logger.warning("LLM response might be truncated")

        text = response_model.result.alternatives[0].message.text
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
