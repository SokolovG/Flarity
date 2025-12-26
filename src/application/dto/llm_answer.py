from msgspec import Struct

from src.application.dto.analysis_result import LLMAnalysisResult


class LLMAnswer(Struct):
    data: LLMAnalysisResult
