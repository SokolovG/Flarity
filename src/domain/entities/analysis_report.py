from msgspec import Struct

from src.domain.entities.log_entry import LogEntry
from src.domain.value_objects.time_range import TimeRange
from src.responses.llm_base_responses import LLMAnalysisResult


class AnalysisReport(Struct):
    has_errors: bool
    time_range: TimeRange
    logs: list[LogEntry] | None = None
    groups: dict[str, list[LogEntry]] | None = None
    llm_analysis: LLMAnalysisResult | None = None


class ErrorGroup(Struct):
    error_type: str
    count: int


class ReportData(Struct):
    title: str
    time_range_hours: TimeRange
    total_errors: int
    logs: list[LogEntry] | None = None
    groups: list[ErrorGroup] | None = None
    unique_types: int | None = None
    ai_analysis: str | None = None
    provider: str | None = None
    tokens_in: int | None = None
    tokens_out: int | None = None
