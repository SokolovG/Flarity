from typing import Self

from pydantic import field_validator, model_validator
from pydantic_settings import BaseSettings, SettingsConfigDict

from src.domain.entities.enums import LLMModel
from src.infrastructure.constants import BASE_DIR

PROMPT_DIR = BASE_DIR / "resources" / "prompts"
BASE_PROMPT_FILE_NAME = "base_prompt.txt"


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
