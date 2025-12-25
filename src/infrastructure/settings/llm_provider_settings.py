from typing import Any

from pydantic import BaseModel
from pydantic_settings import BaseSettings, SettingsConfigDict


class BaseLLMProviderConfig(BaseModel):
    """Base config for all providers."""


class YandexConfig(BaseLLMProviderConfig):
    api_key: str
    catalog_id: str
    base_url: str = "https://llm.api.cloud.yandex.net/foundationModels/v1/completion"


class OllamaConfig(BaseLLMProviderConfig):
    base_url: str = "http://localhost:11434"
    timeout: int = 120


class LLMProviderSettings(BaseSettings):
    provider: str

    config: dict[str, Any] = {}

    model_config = SettingsConfigDict(env_prefix="LLM_PROVIDER_", case_sensitive=False)

    def get_config(self) -> BaseLLMProviderConfig:
        match self.provider:
            case "yandex":
                return YandexConfig(**self.provider_config)
            case "ollama":
                return OllamaConfig(**self.provider_config)
            case _:
                raise ValueError(f"Unknown provider: {self.provider}")
