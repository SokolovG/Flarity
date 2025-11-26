from http import HTTPMethod

import msgspec
from msgspec import Struct

from src.core.constants import YANDEX_GPT_URl
from src.core.decorators import retry
from src.entities.enums import LLMProvider
from src.entities.loki import LogEntry
from src.llm_adapters.base_adapter import BaseLLMAdapter
from src.responses import LLMAnalysisResult, YandexResponse


class _YandexCompletionOptions(Struct):
    stream: bool = False
    temperature: float = 0.6
    maxTokens: str = "2000"


class _YandexMessage(Struct):
    text: str
    role: str = "user"


class _YandexRequest(Struct):
    modelUri: str
    messages: list[_YandexMessage]
    completionOptions: _YandexCompletionOptions


class YandexAdapter(BaseLLMAdapter):
    @retry(max_attempts=5, backoff=10)
    async def anylize_logs(self, logs: list[LogEntry]) -> LLMAnalysisResult:
        yandex_msg_obj = _YandexMessage(text=self.format_logs_for_llm(logs))
        options_obj = _YandexCompletionOptions()
        request = _YandexRequest(
            modelUri=f"gpt://{self.settings.YANDEX_CATALOG_ID}/{self.settings.LLMModel.value}",
            messages=[yandex_msg_obj],
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
        return self._parse_response(response_bytes=response.content)

    def _parse_response(self, response_bytes: bytes) -> LLMAnalysisResult:
        yandex_resp = msgspec.json.decode(response_bytes, type=YandexResponse)
        text = yandex_resp["alternatives"][0]["message"]["text"]
        input_used_token = yandex_resp["usage"]["inputTextTokens"]
        output_used_token = yandex_resp["usage"]["completionTokens"]
        return LLMAnalysisResult(
            analysis_text=text,
            provider=LLMProvider.YANDEX,
            input_tokens_used=input_used_token,
            output_tokens_used=output_used_token,
        )
