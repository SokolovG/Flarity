from abc import ABC, abstractmethod

from src.application.dto.analysis_result import AnalysisResult
from src.domain.entities.log_entry import LogEntry


class LLMAnalyzer(ABC):
    @abstractmethod
    async def analyze(self, logs: list[LogEntry]) -> AnalysisResult: ...
