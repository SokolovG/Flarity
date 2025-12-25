from typing import Any, Self

from pydantic import BaseModel, model_validator
from pydantic_settings import BaseSettings, SettingsConfigDict


class BaseLLMProviderConfig(BaseModel):
    """Base config for all providers."""


class YandexConfig(BaseLLMProviderConfig):
    api_key: str
    catalog_id: str
    base_url: str = "https://llm.api.cloud.yandex.net/foundationModels/v1/completion"

    @model_validator(mode="after")
    def validate_config(self) -> Self:
        if not self.api_key:
            raise ValueError("api_key required")
        return self


class OllamaConfig(BaseLLMProviderConfig):
    base_url: str = "http://localhost:11434"
    timeout: int = 120

    @model_validator(mode="after")
    def validate_config(self) -> Self:
        if not self.base_url:
            raise ValueError("base_url required")
        return self


class LLMProviderSettings(BaseSettings):
    provider: str

    config: dict[str, Any] = {}

    model_config = SettingsConfigDict(
        env_prefix="LLM_PROVIDER_", case_sensitive=False, env_nested_delimiter="__"
    )

    @property
    def get_config(self) -> BaseLLMProviderConfig:
        match self.provider:
            case "yandex":
                return YandexConfig(**self.config)
            case "ollama":
                return OllamaConfig(**self.config)
            case _:
                raise ValueError(f"Unknown provider: {self.provider}")
