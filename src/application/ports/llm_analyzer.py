from abc import ABC, abstractmethod

from src.domain.entities.log_entry import LogEntry
from src.responses.llm_base_responses import LLMAnalysisResult


class LLMAnalyzer(ABC):
    @abstractmethod
    async def analyze(self, logs: list[LogEntry]) -> LLMAnalysisResult: ...
