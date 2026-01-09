import msgspec

from src.application.ports.storage import Storage
from src.infrastructure.constants import LLM_SESSION_PREFIX, TTL_FOR_STORAGE
from src.infrastructure.decorators import log_calls
from src.infrastructure.dto import LLMSession


class ConversationManager:
    def __init__(self, storage: Storage):
        self.storage = storage

    @log_calls
    async def get_session(self, session_id: str) -> LLMSession | None:
        key = f"{LLM_SESSION_PREFIX}{session_id}"
        data = await self.storage.get(key)

        if not data:
            return None

        return msgspec.convert(data, type=LLMSession)

    @log_calls
    async def save_session(
        self, session_id: str, session: LLMSession, ttl: int | None = None
    ) -> None:
        key = f"{LLM_SESSION_PREFIX}{session_id}"
        data = msgspec.to_builtins(session)

        effective_ttl = ttl if ttl is not None else TTL_FOR_STORAGE
        await self.storage.set(key, data, effective_ttl)

    @log_calls
    async def clear_session(self, session_id: str) -> None:
        key = f"{LLM_SESSION_PREFIX}{session_id}"
        await self.storage.delete(key)
