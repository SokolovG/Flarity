from abc import ABC, abstractmethod

from src.clients.http_client import HTTPClient
from src.core.settings import Settings
from src.entities.loki import LogEntry
from src.responses import LLMAnalysisResult


class BaseLLMAdapter(ABC):
    def __init__(self, http_client: HTTPClient, settings: Settings):
        self.http = http_client
        self.settings = settings

    @abstractmethod
    async def analyze_logs(self, logs: list[LogEntry]) -> LLMAnalysisResult: ...

    @abstractmethod
    def _parse_response(self, response_bytes: bytes) -> LLMAnalysisResult: ...

    @staticmethod
    def format_logs_for_llm(logs: list[LogEntry]) -> str:
        logs_text = ""
        for log in logs:
            clean_message = log.message.encode().decode("unicode_escape")
            logs_text += f"[{log.timestamp.strftime('%Y-%m-%d %H:%M:%S')}] {log.level.value} {log.app} {clean_message}\n"

        return logs_text
