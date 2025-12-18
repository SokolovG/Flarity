from msgspec import Struct


class ErrorGroup(Struct):
    error_type: str
    count: int


class ReportData(Struct):
    title: str
    time_range_hours: int
    total_errors: int
    unique_types: int
    ai_analysis: str
    provider: str
    groups: list[ErrorGroup]
    tokens_in: int | None = None
    tokens_out: int | None = None
