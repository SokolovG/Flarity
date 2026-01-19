from typing import Any, Self, overload

from pydantic import BaseModel, field_validator, model_validator
from pydantic_settings import BaseSettings, SettingsConfigDict

from src.domain.entities.enums import LLMModel, NotificationProvider
from src.infrastructure.constants import BASE_DIR, CHAT_ID_FOR_BUG_REPORT

# ============================================================================
# LLM & AI SERVICES
# ============================================================================

PROMPT_DIR = BASE_DIR / "resources" / "prompts"
BASE_PROMPT_FILE_NAME = "base_prompt.txt"


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

    @overload
    def get_config(self, config_type: type[OllamaConfig]) -> OllamaConfig: ...
    @overload
    def get_config(self, config_type: type[YandexConfig]) -> YandexConfig: ...

    def get_config(self, config_type: type[BaseLLMProviderConfig]) -> BaseLLMProviderConfig:
        if config_type == YandexConfig and self.provider != "yandex":
            raise ValueError("LLM provider mismatch!")
        elif config_type == OllamaConfig and self.provider != "ollama":
            raise ValueError("LLM provider mismatch!")

        return config_type(**self.config)


class LLMSettings(BaseSettings):
    model: LLMModel
    temperature: float = 0.6
    max_tokens: int = 1000

    _system_prompt: str = ""

    model_config = SettingsConfigDict(env_prefix="LLM_", case_sensitive=False)

    @field_validator("temperature")
    @classmethod
    def validate_temperature(cls, v: float) -> float:
        if not 0.0 <= v <= 2.0:
            raise ValueError("Temperature must be between 0.0 and 2.0")
        return v

    @field_validator("max_tokens")
    @classmethod
    def validate_max_tokens(cls, v: int) -> int:
        if v < 1 or v > 128000:
            raise ValueError("max_tokens must be between 1 and 128000")
        return v

    @model_validator(mode="after")
    def load_system_prompt(self) -> Self:
        prompt_path = PROMPT_DIR / BASE_PROMPT_FILE_NAME
        if not prompt_path.exists():
            raise FileNotFoundError(
                f"System prompt not found: {prompt_path}\n"
                f"Create the file or check your project structure."
            )

        try:
            self._system_prompt = prompt_path.read_text(encoding="utf-8").strip()
        except Exception as e:
            raise RuntimeError(f"Failed to load system prompt: {e}") from e

        if not self._system_prompt:
            raise ValueError("System prompt is empty")

        return self

    @property
    def system_prompt(self) -> str:
        return self._system_prompt


# ============================================================================
# LOGS
# ============================================================================


class BaseLogsSourceConfig(BaseModel):
    """Base config for all providers."""


class LokiConfig(BaseLogsSourceConfig):
    url: str
    app_name: str


class LogsSourceSettings(BaseSettings):
    provider: str

    config: dict[str, Any] = {}
    model_config = SettingsConfigDict(
        env_prefix="LOG_SOURCE_", case_sensitive=False, env_nested_delimiter="__"
    )

    @overload
    def get_config(self, config_type: type[LokiConfig]) -> LokiConfig: ...

    def get_config(  # ty:ignore[invalid-overload]
        self, config_type: type[BaseLogsSourceConfig]
    ) -> BaseLogsSourceConfig:
        if config_type == LokiConfig and self.provider != "loki":
            raise ValueError("Log source provider mismatch!")

        return config_type(**self.config)


# ============================================================================
# NOTIFICATIONS
# ============================================================================


class BaseNotificationConfig(BaseModel):
    """Base config for all providers."""


class TelegramConfig(BaseNotificationConfig):
    bot_token: str
    chat_id: int | str | None = None
    chat_id_for_bug_report: int | str = CHAT_ID_FOR_BUG_REPORT

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

    @overload
    def get_config(self, config_type: type[TelegramConfig]) -> TelegramConfig: ...

    def get_config(  # ty:ignore[invalid-overload]
        self, config_type: type[BaseNotificationConfig]
    ) -> BaseNotificationConfig:
        if config_type == TelegramConfig and self.provider != NotificationProvider.TELEGRAM:
            raise ValueError("Notification provider mismatch!")

        return config_type(**self.config)
