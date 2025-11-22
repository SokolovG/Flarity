from pydantic_settings import BaseSettings, SettingsConfigDict

from src.entities.enums import LLMProvider


class Settings(BaseSettings):
    LOKI_URL: str
    LOKI_APP_NAME: str
    LOCAL_LLM_URL: str
    LLMProvider: str  # TODO: LLMProvider.value?
    LLMApiKey: str

    model_config = SettingsConfigDict(
        env_file="src/.env", env_file_encoding="utf-8", case_sensitive=True, extra="ignore"
    )


settings = Settings()
