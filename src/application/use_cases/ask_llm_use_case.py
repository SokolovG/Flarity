from src.application.dto.analysis_result import LLMAnalysisResult
from src.application.ports.llm_analyzer import LLMAnalyzer
from src.application.services.conversation_manager import ConversationManager
from src.domain.exceptions import AnalysisFailedError
from src.infrastructure.constants import MAX_RATE_LIMIT_CALLS, MAX_RATE_LIMIT_PERIOD
from src.infrastructure.decorators import log_calls


class AskLLMUseCase:
    def __init__(self, llm_analyzer: LLMAnalyzer, conversation_manager: ConversationManager):
        self.llm = llm_analyzer
        self.conv_manager = conversation_manager

    @log_calls
    async def execute(self, question: str, session_id: str) -> LLMAnalysisResult:
        session = await self.conv_manager.get_session(session_id)
        if not session:
            raise AnalysisFailedError("LLM session is None!")
        session.add_message("user", question)
        answer = await self.llm.ask(question, context=session.messages)
        if not answer:
            raise AnalysisFailedError("LLM returned empty response.")

        return answer
