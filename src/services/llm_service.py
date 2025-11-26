from logging import getLogger

from src.responses import LLMAnalysisResult, LokiQueryResult

logger = getLogger(__name__)


class LLMService:
    def __init__(self) -> None: ...

    async def check_if_llm_is_ready(self) -> bool:
        return True

    async def anylize_logs(self, logs: LokiQueryResult) -> LLMAnalysisResult: ...  # type: ignore
