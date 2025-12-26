from src.application.dto.analysis_report import AnalysisReport
from src.application.dto.llm_answer import LLMAnswer
from src.application.ports.llm_analyzer import LLMAnalyzer
from src.application.ports.log_source import LogSource
from src.domain.services.error_grouper import ErrorGrouper
from src.domain.value_objects.time_range import TimeRange
from src.infrastructure.exceptions.llm_exceptions import LLMError


class AskLLMUseCase:
    def __init__(
        self,
        llm_analyzer: LLMAnalyzer,
    ):
        self.llm = llm_analyzer

    # TODO: add rate limit!
    async def execute(self, question: str) -> ...:
        answer = await self.llm.ask(question)
        if not answer:
            raise LLMError("LLM answer is empty!")

        return LLMAnswer(data=answer.analysis_text)
