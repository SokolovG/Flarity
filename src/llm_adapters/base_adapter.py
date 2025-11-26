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
    async def anylize_logs(self, logs: list[LogEntry]) -> LLMAnalysisResult: ...

    @abstractmethod
    def _parse_response(self, response_bytes: bytes) -> LLMAnalysisResult: ...

    @staticmethod
    def format_logs_for_llm(logs: list[LogEntry]) -> str:
        string = ""
        for log in logs:
            str_log = f"[{log.timestamp.strftime('%Y-%m-%d %H:%M:%S')}] {log.level} {log.app} {log.message} \n"
            string += str_log

        return string
