from typing import Literal

from pydantic_settings import BaseSettings, SettingsConfigDict


class YandexConfig(BaseSettings):
    api_key: str
    catalog_id: str
    base_url: str

    model_config = SettingsConfigDict(env_prefix="YANDEX_")


class OllamaConfig(BaseSettings):
    base_url: str
    timeout: int = 120

    model_config = SettingsConfigDict(env_prefix="OLLAMA_")


class LLMProviderSettings(BaseSettings):
    provider: Literal["yandex", "ollama"]

    model_config = SettingsConfigDict(env_prefix="LLM_")

    @property
    def yandex(self) -> YandexConfig | None:
        if self.provider == "yandex":
            return YandexConfig()
        return None

    @property
    def ollama(self) -> OllamaConfig | None:
        if self.provider == "ollama":
            return OllamaConfig()
        return None
