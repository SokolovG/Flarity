from abc import ABC, abstractmethod

from src.application.dto.analysis_result import LLMAnalysisResult
from src.domain.entities.log_entry import LogEntry
from src.infrastructure.dto import LLMMessage


class LLMAnalyzer(ABC):
    @abstractmethod
    async def analyze(self, logs: list[LogEntry]) -> LLMAnalysisResult: ...
    @abstractmethod
    async def ask(self, question: str, context: list[LLMMessage]) -> LLMAnalysisResult: ...
