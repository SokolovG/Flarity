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
