from typing import Final

import msgspec

from src.application.ports.storage import Storage
from src.infrastructure.dto import LLMSession

LLM_SESSION_PREFIX: Final[str] = "llm:session:"


class ConversationManager:
    def __init__(self, storage: Storage):
        self.storage = storage

    async def get_session(self, session_id: str) -> LLMSession | None:
        key = f"{LLM_SESSION_PREFIX}{session_id}"
        data = await self.storage.get(key)

        if not data:
            return None

        return msgspec.convert(data, type=LLMSession)

    async def save_session(
        self, session_id: str, session: LLMSession, ttl: int | None = None
    ) -> None:
        key = f"{LLM_SESSION_PREFIX}{session_id}"
        data = msgspec.to_builtins(session)

        await self.storage.set(key, data, ttl)
