from http import HTTPMethod

import msgspec
from msgspec import Struct

from src.core.constants import YANDEX_GPT_URl
from src.core.decorators import retry
from src.entities.enums import LLMProvider
from src.entities.loki import LogEntry
from src.exceptions.llm_exceptions import LLMError
from src.llm_adapters.base_adapter import BaseLLMAdapter
from src.responses import LLMAnalysisResult, YandexResponse


class _YandexCompletionOptions(Struct):
    stream: bool = False
    temperature: float = 0.6
    maxTokens: str = "500"


class _YandexMessage(Struct):
    role: str
    text: str


class _YandexRequest(Struct):
    modelUri: str
    completionOptions: _YandexCompletionOptions
    messages: list[_YandexMessage]


class YandexAdapter(BaseLLMAdapter):
    @retry(max_attempts=5, backoff=10)
    async def analyze_logs(self, logs: list[LogEntry]) -> LLMAnalysisResult:
        logs_text = self.format_logs_for_llm(logs=logs, prompt="")
        messages = [
            _YandexMessage(role="system", text=self.settings.get_system_prompt),
            _YandexMessage(role="user", text=logs_text),
        ]
        options_obj = _YandexCompletionOptions()
        request = _YandexRequest(
            modelUri=f"gpt://{self.settings.YANDEX_CATALOG_ID}/{self.settings.LLMModel.value}",
            messages=[messages],
            completionOptions=options_obj,
        )
        data = msgspec.json.encode(request)
        response = await self.http.make_request(
            method=HTTPMethod.POST,
            url=YANDEX_GPT_URl,
            headers={
                "Authorization": f"Api-Key {self.settings.YANDEX_API_KEY}",
                "Content-Type": "application/json",
            },
            data=data,
        )

        if response.status_code != 200:
            error_text = response.text
            raise LLMError(
                f"Yandex API error: {response.status_code}", details={"response": error_text}
            )

        return self._parse_response(response_bytes=response.content)

    def _parse_response(self, response_bytes: bytes) -> LLMAnalysisResult:
        response_model = msgspec.json.decode(response_bytes, type=YandexResponse)
        text = response_model.result.alternatives[0].message.text
        input_used_token = response_model.result.usage.inputTextTokens
        output_used_token = response_model.result.usage.completionTokens

        return LLMAnalysisResult(
            analysis_text=text,
            provider=LLMProvider.YANDEX,
            input_tokens_used=int(input_used_token),
            output_tokens_used=int(output_used_token),
        )
