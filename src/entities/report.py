from msgspec import Struct


class AnalysisResult(Struct):
    has_errors: bool
    report_html: str
    hours: int


class ErrorGroup(Struct):
    error_type: str
    count: int


class ReportData(Struct):
    title: str
    time_range_hours: int
    total_errors: int
    groups: list[ErrorGroup] | None = None
    unique_types: int | None = None
    ai_analysis: str | None = None
    provider: str | None = None
    tokens_in: int | None = None
    tokens_out: int | None = None
