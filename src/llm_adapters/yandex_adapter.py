from http import HTTPMethod, HTTPStatus
from logging import getLogger

import msgspec

from src.core.decorators import retry
from src.entities.enums import LLMModel, LLMProvider
from src.entities.loki import LogEntry
from src.exceptions.llm_exceptions import LLMAuthError, LLMError, LLMRateLimitError
from src.llm_adapters.base_adapter import BaseLLMAdapter
from src.responses import LLMAnalysisResult, YandexResponse

logger = getLogger(__name__)


class YandexAdapter(BaseLLMAdapter):
    @retry(max_attempts=5, backoff=10, retryable_exceptions=(LLMError, LLMRateLimitError))
    async def analyze_logs(self, logs: list[LogEntry]) -> LLMAnalysisResult:
        logs_text = self.format_logs_for_llm(logs=logs)
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
        response = await self.http.make_request(
            method=HTTPMethod.POST,
            url=self.settings.llm_provider.yandex.base_url,
            headers={
                "Authorization": f"Api-Key {self.settings.llm_provider.yandex.api_key}",
                "Content-Type": "application/json",
            },
            data=request_data,
        )
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

        return self._parse_response(response_bytes=response.content)

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
            f"gpt://{self.settings.llm_provider.yandex.api_key}/{self.settings.llm.model.value}"
        )
        match self.settings.llm.model:
            case LLMModel.YANDEX_GPT_5:
                modelUri += "latest"
            case LLMModel.YANDEX_GPT_PRO_5_1:
                modelUri += "rc"
        return modelUri
