from http import HTTPStatus
from logging import getLogger
from typing import Any

import msgspec
from httpx import Response

from src.core.exceptions import LLMAuthError, LLMError, LLMRateLimitError
from src.domain.entities.enums import LLMModel
from src.domain.entities.log_entry import LogEntry
from src.infrastructure.llm.base_http_llm_analyzer import BaseHTTPLLMAnalyzer
from src.infrastructure.llm.providers import LLMProvider
from src.responses import LLMAnalysisResult, YandexResponse

logger = getLogger(__name__)


class YandexAnalyzer(BaseHTTPLLMAnalyzer):
    def _get_api_url(self) -> str:
        url = self.settings.llm_provider.yandex.base_url
        return url

    def _get_headers(self) -> dict[str, Any]:
        headers = {
            "Authorization": f"Api-Key {self.settings.llm_provider.yandex.api_key}",
            "Content-Type": "application/json",
        }
        return headers

    def _build_request(self, logs_text: str) -> dict[str, Any]:
        request_data = {
            "modelUri": self._get_model_uri(),
            "completionOptions": {
                "stream": False,
                "temperature": self.settings.llm.temperature,
                "maxTokens": self.settings.llm.max_tokens,
            },
            "messages": [
                {"role": "system", "text": self.settings.llm.system_prompt},
                {"role": "user", "text": logs_text},
            ],
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

    def _parse_response(self, response_bytes: bytes) -> LLMAnalysisResult:
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
            analysis_text=text,
            provider=LLMProvider.YANDEX,
            input_tokens_used=int(input_used_token),
            output_tokens_used=int(output_used_token),
        )

    def _get_model_uri(self) -> str:
        modelUri = (
            f"gpt://{self.settings.llm_provider.yandex.catalog_id}/{self.settings.llm.model.value}"
        )
        match self.settings.llm.model:
            case LLMModel.YANDEX_GPT_5:
                modelUri += "latest"
            case LLMModel.YANDEX_GPT_PRO_5_1:
                modelUri += "rc"
        return modelUri

    def _format_logs_for_llm(self, logs: list[LogEntry]) -> str:
        logs_text = ""
        for log in logs:
            clean_message = log.message.encode().decode("unicode_escape")
            logs_text += f"[{log.timestamp.strftime('%Y-%m-%d %H:%M:%S')}] {log.level.value} {log.app} {clean_message}\n"

        return logs_text
