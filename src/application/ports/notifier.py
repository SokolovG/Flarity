from abc import ABC, abstractmethod
from typing import Any

from aiogram.types import InlineKeyboardMarkup


class Notifier(ABC):
    @abstractmethod
    async def send(
        self,
        message: str,
        chat_id: str | None = None,
        reply_markup: InlineKeyboardMarkup | None = None,
        return_message_details: bool | None = False,
    ) -> bool | Any: ...
