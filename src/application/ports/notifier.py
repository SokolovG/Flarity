from abc import ABC, abstractmethod

from aiogram.types import InlineKeyboardMarkup


class Notifier(ABC):
    @abstractmethod
    async def send(
        self,
        message: str,
        chat_id: str | None = None,
        reply_markup: InlineKeyboardMarkup | None = None,
    ) -> bool: ...
