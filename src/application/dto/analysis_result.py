from typing import Self

from msgspec import Struct

from src.core.utils import format_time_range
from src.domain.value_objects.time_range import TimeRange
from src.infrastructure.llm.providers import LLMProvider


class LLMAnalysisResult(Struct):
    analysis_text: str
    provider: LLMProvider
    input_tokens_used: int | None = None
    output_tokens_used: int | None = None


class AnalysisResult(Struct):
    has_errors: bool
    report_html: str
    hours: TimeRange

    @staticmethod
    def no_errors(time_range: TimeRange) -> "AnalysisResult":
        return AnalysisResult(
            has_errors=False,
            report_html=f"✅ No errors in last {time_range.hours} {format_time_range(time_range)}",
            hours=time_range,
        )
