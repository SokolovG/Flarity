from typing import Self

from pydantic import model_validator
from pydantic_settings import BaseSettings, SettingsConfigDict

from src.entities.enums import LLMModel, LLMProvider


class Settings(BaseSettings):
    LOKI_URL: str
    LOKI_APP_NAME: str
    LOCAL_LLM_URL: str
    LLMProvider: LLMProvider
    LLMModel: LLMModel
    YANDEX_API_KEY: str | None
    YANDEX_CATALOG_ID: str | None
    GIGACHAT_API_KEY: str | None
    LLM_TEMPERATURE: float

    model_config = SettingsConfigDict(
        env_file=".env", env_file_encoding="utf-8", case_sensitive=True, extra="ignore"
    )

    @model_validator(mode="after")
    def validate_api_keys(self) -> Self:
        match self.LLMProvider:
            case LLMProvider.YANDEX:
                if not self.YANDEX_API_KEY:
                    raise ValueError(f"For {LLMProvider.YANDEX} YANDEX_API_KEY is empty")

            case LLMProvider.GIGACHAT:
                if not self.GIGACHAT_API_KEY:
                    raise ValueError(f"For {LLMProvider.GIGACHAT} GIGACHAT_API_KEY is empty")
        return self

    @property
    def get_api_key(self) -> str:
        match self.LLMProvider:
            case LLMProvider.YANDEX:
                key = self.YANDEX_API_KEY
                assert key is not None, "Validated in model_validator"
                return key
            case LLMProvider.GIGACHAT:
                key = self.GIGACHAT_API_KEY
                assert key is not None, "Validated in model_validator"
                return key
            case _:
                return ""
