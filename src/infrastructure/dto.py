from datetime import datetime

from msgspec import Struct, field


class BaseInfrastructureObject(Struct):
    pass


class LLMMessage(BaseInfrastructureObject):
    role: str  # "user" | "assistant"
    text: str


class TelegramMessage(BaseInfrastructureObject):
    message_id: int
    chat_id: int


class LLMSession(BaseInfrastructureObject):
    messages: list[LLMMessage] = field(default_factory=list)
    created_at: datetime = field(default_factory=datetime.now)

    def add_message(self, role: str, text: str) -> None:
        self.messages.append(LLMMessage(role=role, text=text))

    def add_bulk_messages(self, messages: list[LLMMessage]) -> None:
        for msg in messages:
            self.messages.append(msg)
