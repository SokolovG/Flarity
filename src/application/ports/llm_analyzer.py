from abc import ABC, abstractmethod

from src.core.settings.app_settings import AppSettings
from src.domain.entities.log_entry import LogEntry
from src.infrastructure.clients.http_client import HTTPClient
from src.responses.llm_base_responses import LLMAnalysisResult


class LLMAnalyzer(ABC):
    def __init__(self, http_client: HTTPClient, settings: AppSettings):
        self.http = http_client
        self.settings = settings

    @abstractmethod
    async def analyze(self, logs: list[LogEntry]) -> LLMAnalysisResult: ...

    @staticmethod
    def format_logs_for_llm(logs: list[LogEntry]) -> str:
        logs_text = ""
        for log in logs:
            clean_message = log.message.encode().decode("unicode_escape")
            logs_text += f"[{log.timestamp.strftime('%Y-%m-%d %H:%M:%S')}] {log.level.value} {log.app} {clean_message}\n"

        return logs_text
