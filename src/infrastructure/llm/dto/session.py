from datetime import datetime

from msgspec import field

from src.infrastructure.base_dto import BaseInfrastructureObject


class LLMMessage(BaseInfrastructureObject):
    role: str  # "user" | "assistant"
    text: str


class LLMSession(BaseInfrastructureObject):
    messages: list[LLMMessage] = field(default_factory=list)
    created_at: datetime = field(default_factory=datetime.now)

    def add_message(self, role: str, text: str) -> None:
        self.messages.append(LLMMessage(role=role, text=text))

    def add_bulk_messages(self, messages: list[LLMMessage]) -> None:
        for msg in messages:
            self.messages.append(msg)
