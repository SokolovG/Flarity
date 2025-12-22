import re
from http import HTTPMethod, HTTPStatus
from logging import getLogger

import msgspec

from src.entities.enums import LLMProvider
from src.entities.loki import LogEntry
from src.exceptions.llm_exceptions import LLMError
from src.llm_adapters.base_adapter import BaseLLMAdapter
from src.responses import LLMAnalysisResult, OllamaErrorResponse, OllamaResponse

logger = getLogger(__name__)


class OllamaAdapter(BaseLLMAdapter):
    async def analyze_logs(self, logs: list[LogEntry]) -> LLMAnalysisResult:
        logs_text = self.format_logs_for_llm(logs)
        request_data = {
            "model": self.settings.llm.model,
            "messages": [
                {"role": "system", "content": self.settings.llm.system_prompt},
                {"role": "user", "content": logs_text},
            ],
            "stream": False,
            "options": {"num_predict": self.settings.llm.max_tokens},
        }

        response = await self.http.make_request(
            url=f"{self.settings.llm_provider.ollama.base_url}/api/chat",
            method=HTTPMethod.POST,
            data=request_data,
            timeout=self.settings.llm_provider.ollama.timeout,
            no_log_answer=True,
        )

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

        return self._parse_response(response_bytes=response.content)

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
