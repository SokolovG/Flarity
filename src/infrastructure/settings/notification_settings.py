from typing import Any, overload

from pydantic import BaseModel, field_validator
from pydantic_settings import BaseSettings, SettingsConfigDict

from src.domain.entities.enums import NotificationProvider


class BaseNotificationConfig(BaseModel):
    """Base config for all providers."""


class TelegramConfig(BaseNotificationConfig):
    bot_token: str
    chat_id: int | str | None = None

    @field_validator("bot_token")
    @classmethod
    def validate_bot_token(cls, v: str) -> str:
        if not v or len(v) < 20:
            raise ValueError("Invalid Telegram bot token")
        if not v.count(":") == 1:
            raise ValueError("Bot token must contain exactly one ':'")
        return v


class NotificationSettings(BaseSettings):
    provider: NotificationProvider
    config: dict[str, Any] = {}

    model_config = SettingsConfigDict(
        env_prefix="NOTIFICATION_", case_sensitive=False, env_nested_delimiter="__"
    )

    @overload  # type: ignore[misc]
    def get_config(self, config_type: type[TelegramConfig]) -> TelegramConfig: ...

    def get_config(self, config_type: type[BaseNotificationConfig]) -> BaseNotificationConfig:
        if config_type == TelegramConfig and self.provider != NotificationProvider.TELEGRAM:
            raise ValueError("Notification provider mismatch!")

        return config_type(**self.config)
