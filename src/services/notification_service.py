from typing import Literal

from src.clients import TelegramClient
from src.core.settings.notification_settings import NotificationSettings
from src.entities.report import ReportData
from src.services.base_services import BaseNotificationService


class NotificationService(BaseNotificationService):
    def __init__(self, telegram_client: TelegramClient, settings: NotificationSettings):
        self.telegram_client = telegram_client
        self.settings = settings

    async def send_message(
        self,
        message: str,
        parse_mode: Literal["HTML", "Markdown", "MarkdownV2"] = "HTML",
        chat_id: str | None = None,
    ) -> bool:
        return await self.telegram_client.send_message(message, parse_mode, chat_id)
