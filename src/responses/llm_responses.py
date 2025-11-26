from msgspec import Struct

from src.entities.enums import LLMProvider


class LLMAnalysisResult(Struct):
    analysis_text: str
    provider: LLMProvider
    tokens_used: int | None = None
