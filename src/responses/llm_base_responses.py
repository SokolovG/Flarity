from msgspec import Struct

from src.infrastructure.llm.providers import LLMProvider


class LLMAnalysisResult(Struct):
    analysis_text: str
    provider: LLMProvider
    input_tokens_used: int | None = None
    output_tokens_used: int | None = None
