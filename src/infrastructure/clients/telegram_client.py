from http import HTTPMethod, HTTPStatus
from typing import Any

from aiogram.types import InlineKeyboardMarkup
from httpx import Response

from src.infrastructure.clients.http_client import HTTPClient
from src.infrastructure.constants import TELEGRAM_MESSAGE_LIMIT
from src.infrastructure.entities import TelegramMessage
from src.infrastructure.enums import TextType
from src.infrastructure.exceptions import (
    TelegramBadRequestError,
    TelegramError,
    TelegramRateLimitError,
)
from src.infrastructure.settings.notification_settings import NotificationSettings, TelegramConfig


class TelegramClient:
    def __init__(self, http_client: HTTPClient, settings: NotificationSettings):
        self._http = http_client
        self.settings = settings
        self.config = settings.get_config(TelegramConfig)

    @property
    def _base_url(self) -> str:
        return f"https://api.telegram.org/bot{self.config.bot_token}"

    async def send_message(
        self,
        text: str,
        parse_mode: TextType | None = TextType.HTML,
        chat_id: str | None = None,
        reply_markup: InlineKeyboardMarkup | None = None,
    ) -> TelegramMessage:
        if not text or len(text.strip()) == 0:
            raise ValueError("Message text is empty")
        # TODO: fck ** in telegram report! fix it.
        if len(text) > TELEGRAM_MESSAGE_LIMIT:
            messages: list[TelegramMessage] = []
            chunks = self._split_message(text)
            for i, chunk in enumerate(chunks):
                markup = reply_markup if i == len(chunks) - 1 else None
                msg = await self._send_single_message(
                    chunk,
                    parse_mode=parse_mode,
                    chat_id=chat_id,
                    reply_markup=markup,
                )
                messages.append(msg)

            return messages[-1]

        return await self._send_single_message(
            text,
            parse_mode=parse_mode,
            chat_id=chat_id,
            reply_markup=reply_markup,
        )

    async def _send_single_message(
        self,
        text: str,
        parse_mode: TextType | None = TextType.HTML,
        chat_id: str | None = None,
        reply_markup: InlineKeyboardMarkup | None = None,
    ) -> TelegramMessage:
        data = {
            "text": text,
            "chat_id": chat_id if chat_id else self.config.chat_id,
            "parse_mode": parse_mode.value,  # type: ignore
        }

        if reply_markup:
            data["reply_markup"] = reply_markup.model_dump(exclude_none=True)

        response = await self._http.make_request(
            method=HTTPMethod.POST,
            url=f"{self._base_url}/sendMessage",
            data=data,
            timeout=10,
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

        return self._parse_message_details(response)

    def _parse_message_details(self, response: Response) -> TelegramMessage:
        response_data = response.json()
        result = response_data.get("result")

        if not result:
            raise TelegramError("Invalid Telegram API response: missing 'result'")

        chat = result.get("chat")
        if not chat:
            raise TelegramError("Invalid Telegram API response: missing 'chat'")

        msg = TelegramMessage(
            message_id=result.get("message_id"),
            chat_id=chat.get("id"),
        )
        return msg

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
