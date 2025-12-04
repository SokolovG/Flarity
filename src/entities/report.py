from msgspec import Struct


class ReportData(Struct):
    title: str
    time_range_hours: int
    total_errors: int
    unique_types: int
    ai_analysis: str
    # top_errors: list[tuple[str, int]]
    provider: str
    tokens_in: int | None = None
    tokens_out: int | None = None
