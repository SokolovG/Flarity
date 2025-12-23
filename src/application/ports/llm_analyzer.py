from abc import ABC, abstractmethod
from typing import Any

from httpx import Response

from src.core.settings.app_settings import AppSettings
from src.domain.entities.log_entry import LogEntry
from src.infrastructure.clients.http_client import HTTPClient
from src.responses.llm_base_responses import LLMAnalysisResult


class LLMAnalyzer(ABC):
    @abstractmethod
    async def analyze(self, logs: list[LogEntry]) -> LLMAnalysisResult: ...
    @abstractmethod
    def _build_request(self, logs: list[LogEntry]) -> dict[str, Any]: ...
    @abstractmethod
    def _handle_response(self, response: Response) -> None: ...
    @abstractmethod
    def _parse_response(self, response_bytes: bytes) -> LLMAnalysisResult: ...
    @abstractmethod
    def _format_logs_for_llm(self, logs: list[LogEntry]) -> str: ...
