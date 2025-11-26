from http import HTTPMethod
from logging import getLogger

import msgspec

from src.clients.base_client import BaseClient
from src.core.constants import YANDEX_GPT_URl
from src.core.decorators import retry
from src.entities.llm import CompletionOptions, LLMRequest, Message
from src.exceptions.llm_exceptions import LLMError
from src.responses import LLMResponse, LokiQueryResult

logger = getLogger(__name__)


class LLMClient(BaseClient):
    async def is_llm_is_ready(self) -> bool:
        return True

    @retry(max_attempts=5, backoff=10)
    async def send_request_to_llm(self, logs: LokiQueryResult) -> LLMResponse:
        API_KEY = "CHOOSE API KEY"
        headers = {"Content-Type": "application/json", "Authorization": API_KEY}
        completion_options = CompletionOptions()
        message = Message(
            text=str(logs.logs)  # TODO: transfer to str?
        )
        data = LLMRequest(
            modelUri="",  # TODO: str with model and catalog
            completionOptions=completion_options,
            messages=message,
        )
        # transfer data to dict!
        response = await self._http.make_request(
            headers=headers, method=HTTPMethod.POST, url=YANDEX_GPT_URl, data=data
        )

        if response.status_code >= 500:
            raise LLMError(f"Loki server error: {response.status_code}")
        elif response.status_code >= 400:
            raise LLMError(f"Bad request: {response.status_code}")

        llm_response: LLMResponse = msgspec.json.decode(response.content, type=LLMResponse)
        return llm_response
