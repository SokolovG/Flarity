import msgspec

from src.application.ports.session_storage import SessionStorage
from src.infrastructure.entities import LLMSession


class ConversationManager:
    def __init__(self, storage: SessionStorage):
        self.storage = storage

    async def get_session(self, session_id: str) -> LLMSession | None:
        key = f"llm:session:{session_id}"
        data = await self.storage.get(key)

        if not data:
            return None

        return msgspec.convert(data, type=LLMSession)

    async def save_session(
        self, session_id: str, session: LLMSession, ttl: int | None = None
    ) -> None:
        key = f"llm:session:{session_id}"
        data = msgspec.to_builtins(session)

        await self.storage.set(key, data, ttl)

    async def add_user_message(self, question: str, session_id: str) -> ...: ...
    async def add_assistant_message(self, session_id: str, answer: str) -> ...: ...
    async def clear_session(self, session_id: str) -> ...: ...
