from msgspec import Struct


class BaseMessageObject(Struct):
    pass


class TelegramMessage(BaseMessageObject):
    message_id: int
    chat_id: int
