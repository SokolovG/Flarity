from msgspec import Struct

from src.application.dto.analysis_result import LLMAnalysisResult
from src.domain.entities.log_entry import LogEntry
from src.domain.value_objects.time_range import TimeRange
from src.infrastructure.dto import LLMMessage


class AnalysisReport(Struct):
    has_errors: bool
    time_range: TimeRange
    logs: list[LogEntry] | None = None
    groups: dict[str, list[LogEntry]] | None = None
    llm_analysis: LLMAnalysisResult | None = None
    messages: list[LLMMessage] | None = None


class ErrorGroup(Struct):
    error_type: str
    count: int
