from src.application.dto.llm_answer import LLMAnswer
from src.application.ports.llm_analyzer import LLMAnalyzer
from src.domain.exceptions import AnalysisFailedError


class AskLLMUseCase:
    def __init__(
        self,
        llm_analyzer: LLMAnalyzer,
    ):
        self.llm = llm_analyzer

    # TODO: add rate limit!
    async def execute(self, question: str) -> LLMAnswer:
        answer = await self.llm.ask(question)
        if not answer:
            raise AnalysisFailedError("LLM returned empty response.")

        return LLMAnswer(data=answer.analysis_text)
