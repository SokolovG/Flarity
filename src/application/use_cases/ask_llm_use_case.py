from src.application.dto.analysis_result import LLMAnalysisResult
from src.application.ports.llm_analyzer import LLMAnalyzer
from src.domain.constants import MAX_QUESTIONS_PER_SESSION
from src.domain.exceptions import AnalysisFailedError, LLMChatLimitExceededError
from src.infrastructure.constants import (
    RATE_LIMIT_ASK_LLM_CALLS,
    RATE_LIMIT_ASK_LLM_PERIOD,
    RATE_LIMITER_ASK_LLM_PREFIX,
)
from src.infrastructure.decorators import log_calls
from src.infrastructure.rate_limiter import RateLimiter
from src.infrastructure.services.conversation_manager import ConversationManager


# TODO: докинуть везде лог левел в exceptions
class AskLLMUseCase:
    def __init__(
        self,
        llm_analyzer: LLMAnalyzer,
        conversation_manager: ConversationManager,
        limiter: RateLimiter,
    ):
        self.llm = llm_analyzer
        self.conv_manager = conversation_manager
        self.limiter = limiter

    @log_calls
    async def execute(self, question: str, user_id: str) -> LLMAnalysisResult:
        await self.limiter.check_limit(
            user_id,
            prefix=RATE_LIMITER_ASK_LLM_PREFIX,
            calls=RATE_LIMIT_ASK_LLM_CALLS,
            period=RATE_LIMIT_ASK_LLM_PERIOD,
        )
        session = await self.conv_manager.get_session(user_id)
        if not session:
            raise AnalysisFailedError("LLM session is None!")

        question_count = len([m for m in session.messages if m.role == "user"])
        if question_count >= MAX_QUESTIONS_PER_SESSION:
            raise LLMChatLimitExceededError(
                message=f"Exceeded limit of {MAX_QUESTIONS_PER_SESSION} questions",
                details={"limit": MAX_QUESTIONS_PER_SESSION},
            )

        session.add_message("user", question)

        answer = await self.llm.ask(context=session.messages)
        if not answer:
            raise AnalysisFailedError("LLM returned empty response.")

        session.add_message("assistant", answer.analysis_text)
        await self.conv_manager.save_session(user_id, session)

        return answer
