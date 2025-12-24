from abc import ABC, abstractmethod
from http import HTTPMethod
from typing import Any

from httpx import Response

from src.application.dto.analysis_result import AnalysisResult, LLMAnalysisResult
from src.application.ports.llm_analyzer import LLMAnalyzer
from src.core.settings.app_settings import AppSettings
from src.domain.entities.log_entry import LogEntry
from src.infrastructure.clients.http_client import HTTPClient


class BaseHTTPLLMAnalyzer(LLMAnalyzer, ABC):
    def __init__(self, http_client: HTTPClient, settings: AppSettings):
        self.http = http_client
        self.settings = settings

    async def analyze(self, logs: list[LogEntry]) -> AnalysisResult:
        formatted_logs = self._format_logs_for_llm(logs)
        request_data = self._build_request(formatted_logs)
        response = await self._make_http_request(request_data)
        self._handle_response(response)
        return self._parse_response(response.content)

    @abstractmethod
    def _build_request(self, logs_text: str) -> dict[str, Any]: ...
    @abstractmethod
    def _get_headers(self) -> dict[str, Any]: ...
    @abstractmethod
    def _handle_response(self, response: Response) -> None: ...
    @abstractmethod
    def _parse_response(self, response_bytes: bytes) -> LLMAnalysisResult: ...
    @abstractmethod
    def _get_api_url(self) -> str: ...

    def _format_logs_for_llm(self, logs: list[LogEntry]) -> str:
        logs_text = ""
        for log in logs:
            clean_message = log.message.encode().decode("unicode_escape")
            logs_text += f"[{log.timestamp}] {log.level.value} {clean_message}\n"
        return logs_text

    async def _make_http_request(self, data: dict) -> Response:
        return await self.http.make_request(
            method=HTTPMethod.POST,
            url=self._get_api_url(),
            data=data,
            headers=self._get_headers(),
        )
