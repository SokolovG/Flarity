from src.application.ports.notifier import Notifier
from src.core.settings.notification_settings import NotificationSettings
from src.infrastructure.clients.telegram_client import TelegramClient


class TelegramNotifier(Notifier):
    def __init__(self, telegram_client: TelegramClient, settings: NotificationSettings):
        self.telegram_client = telegram_client
        self.settings = settings

    # TODO: Добавить reply_markup параметр к send_message()? иначе не получается добавить клаву к длинному сообщению
    async def send(self, message: str, chat_id: str | None = None) -> bool:
        return await self.telegram_client.send_message(message, chat_id=chat_id)
