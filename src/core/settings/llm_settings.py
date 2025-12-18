from typing import Self

from pydantic import model_validator
from pydantic_settings import BaseSettings, SettingsConfigDict

from src.entities.enums import LLMModel


class LLMSettings(BaseSettings):
    model: LLMModel
    temperature: float = 0.6
    max_tokens: int = 1000

    _system_prompt: str = ""

    model_config = SettingsConfigDict(env_prefix="LLM_")

    @model_validator(mode="after")
    def load_system_prompt(self) -> Self:
        with open("prompts/base_prompt.txt", "r") as f:
            self._system_prompt = f.read()
        return self

    @property
    def system_prompt(self) -> str:
        return self._system_prompt
