from http import HTTPMethod, HTTPStatus

from src.infrastructure.clients.http_client import HTTPClient
from src.infrastructure.constants import TELEGRAM_MESSAGE_LIMIT
from src.infrastructure.exceptions import (
    TelegramBadRequestError,
    TelegramError,
    TelegramRateLimitError,
)
from src.infrastructure.settings.notification_settings import NotificationSettings


class TelegramClient:
    def __init__(self, http_client: HTTPClient, settings: NotificationSettings):
        self._http = http_client
        self.settings = settings

    @property
    def _base_url(self) -> str:
        return f"https://api.telegram.org/bot{self.settings.get_config.bot_id}"

    async def send_message(
        self, text: str, parse_mode: str = "HTML", chat_id: str | None = None
    ) -> bool:
        if not text or len(text.strip()) == 0:
            raise ValueError("Message text is empty")

        if len(text) > TELEGRAM_MESSAGE_LIMIT:
            chunks = self._split_message(text)
            for chunk in chunks:
                await self._send_single_message(chunk, parse_mode=parse_mode, chat_id=chat_id)
            return True

        return await self._send_single_message(text, parse_mode=parse_mode, chat_id=chat_id)

    async def _send_single_message(
        self, text: str, parse_mode: str = "HTML", chat_id: str | None = None
    ) -> bool:
        data = {
            "text": text,
            "chat_id": chat_id if chat_id else self.settings.get_config.chat_id,
            "parse_mode": parse_mode,
        }
        response = await self._http.make_request(
            method=HTTPMethod.POST,
            url=f"https://api.telegram.org/bot{self.settings.get_config.bot_id}/sendMessage",
            data=data,
            no_log_answer=True,
        )

        if response.status_code != HTTPStatus.OK:
            if response.status_code == HTTPStatus.SERVICE_UNAVAILABLE:
                raise TelegramError("Telegram is temporarily unavailable")
            elif response.status_code >= HTTPStatus.INTERNAL_SERVER_ERROR:
                raise TelegramError(f"Telegram server error: {response.status_code}")
            elif response.status_code == HTTPStatus.TOO_MANY_REQUESTS:
                raise TelegramRateLimitError(
                    "Rate limit exceeded", details={"status": response.status_code}
                )
            elif response.status_code >= 400:
                raise TelegramBadRequestError(f"Bad request: {response.status_code}")
        return True

    @staticmethod
    def _split_message(text: str, max_length: int = 4096) -> list[str]:
        chunks = []
        while len(text) > max_length:
            split_pos = text.rfind("\n", 0, max_length)
            if split_pos == -1:
                split_pos = max_length

            chunks.append(text[:split_pos])
            text = text[split_pos:].lstrip()

        if text:
            chunks.append(text)

        return chunks
