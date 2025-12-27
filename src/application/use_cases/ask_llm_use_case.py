from ratelimit import limits

from src.application.dto.analysis_result import LLMAnalysisResult
from src.application.ports.llm_analyzer import LLMAnalyzer
from src.domain.exceptions import AnalysisFailedError
from src.infrastructure.constants import MAX_RATE_LIMIT_CALLS, MAX_RATE_LIMIT_PERIOD


class AskLLMUseCase:
    def __init__(
        self,
        llm_analyzer: LLMAnalyzer,
    ):
        self.llm = llm_analyzer

    @limits(calls=MAX_RATE_LIMIT_CALLS, period=MAX_RATE_LIMIT_PERIOD)
    async def execute(self, question: str, session_id: str) -> LLMAnalysisResult:
        answer = await self.llm.ask(question, session_id)
        if not answer:
            raise AnalysisFailedError("LLM returned empty response.")

        return answer
