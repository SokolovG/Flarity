from pydantic_settings import BaseSettings, SettingsConfigDict

from src.entities.enums import LLMModel, LLMProvider


class Settings(BaseSettings):
    LOKI_URL: str
    LOKI_APP_NAME: str
    LOCAL_LLM_URL: str
    LLMProvider: LLMProvider
    LLMModel: LLMModel
    YandexApiKey: str | None
    SberApiKey: str | None
    LLM_TEMPERATURE: float

    model_config = SettingsConfigDict(
        env_file=".env", env_file_encoding="utf-8", case_sensitive=True, extra="ignore"
    )
