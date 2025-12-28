from datetime import datetime

from msgspec import Struct
from pydantic import Field


class BaseMessageObject(Struct):
    pass


class LLMMessage(BaseMessageObject):
    role: str
    content: str


class TelegramMessage(BaseMessageObject):
    message_id: int
    chat_id: int


class LLMSession(BaseMessageObject):
    messages: list[LLMMessage] = Field(default_factory=list)
    created_at: datetime = Field(default_factory=datetime.now)

    def add_message(self, role: str, content: str) -> None:
        self.messages.append(LLMMessage(role=role, content=content))
