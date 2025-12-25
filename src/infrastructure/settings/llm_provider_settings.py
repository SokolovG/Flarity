from typing import Literal

from pydantic import BaseModel
from pydantic_settings import BaseSettings, SettingsConfigDict


class YandexConfig(BaseModel):
    api_key: str
    catalog_id: str
    base_url: str


class OllamaConfig(BaseModel):
    base_url: str
    timeout: int = 120


class LLMProviderSettings(BaseSettings):
    provider: Literal["yandex", "ollama"]

    yandex_api_key: str = ""
    yandex_catalog_id: str = ""
    yandex_base_url: str = "https://llm.api.cloud.yandex.net/foundationModels/v1/completion"

    ollama_base_url: str = "http://localhost:11434"
    ollama_timeout: int = 120

    model_config = SettingsConfigDict(env_prefix="LLM_PROVIDER_", case_sensitive=False)

    @property
    def yandex(self) -> YandexConfig:
        return YandexConfig(
            api_key=self.yandex_api_key,
            catalog_id=self.yandex_catalog_id,
            base_url=self.yandex_base_url,
        )

    @property
    def ollama(self) -> OllamaConfig:
        return OllamaConfig(base_url=self.ollama_base_url, timeout=self.ollama_timeout)
