from aiogram.types import InlineKeyboardMarkup

from src.application.ports.notifier import Notifier
from src.infrastructure.clients.telegram_client import TelegramClient
from src.infrastructure.constants import TextType
from src.infrastructure.dto import TelegramMessage
from src.infrastructure.settings.notification_settings import NotificationSettings


class TelegramNotifier(Notifier):
    def __init__(self, telegram_client: TelegramClient, settings: NotificationSettings):
        self.telegram_client = telegram_client
        self.settings = settings

    async def send(  # type: ignore
        self,
        message: str,
        chat_id: str | None = None,
        parse_mode: TextType | None = TextType.HTML,
        reply_markup: InlineKeyboardMarkup | None = None,
    ) -> TelegramMessage:
        return await self.telegram_client.send_message(
            message,
            parse_mode=parse_mode,
            chat_id=chat_id,
            reply_markup=reply_markup,
        )
