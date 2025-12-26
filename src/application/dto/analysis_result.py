from msgspec import Struct

from src.domain.entities.enums import LLMProvider


class LLMAnalysisResult(Struct):
    analysis_text: str
    provider: LLMProvider
    input_tokens_used: int | None = None
    output_tokens_used: int | None = None
