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
