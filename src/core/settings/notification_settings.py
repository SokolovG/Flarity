from pydantic_settings import BaseSettings, SettingsConfigDict


class NotificationSettings(BaseSettings):
    telegram_bot_token: str
    telegram_chat_id: str

    model_config = SettingsConfigDict(env_prefix="TELEGRAM_")
