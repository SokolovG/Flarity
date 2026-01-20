from src.infrastructure.base_dto import BaseInfrastructureObject


class TelegramMessage(BaseInfrastructureObject):
    message_id: int
    chat_id: int
