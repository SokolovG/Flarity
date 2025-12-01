from enum import Enum


class LLMProvider(Enum):
    OLLAMA = "ollama"
    YANDEX = "yandex"


class LLMModel(Enum):
    YANDEX_GPT_LITE = "yandexgpt-lite"
    YANDEX_GPT_PRO_5_1 = "yandexgpt"
    YANDEX_GPT_5 = "yandexgpt"
    ALICE_LLM = "aliceai-llm"


class LogLevel(Enum):
    INFO = "info"
    WARNING = "warning"
    ERROR = "error"
    CRITICAL = "critical"


class Directions(Enum):
    BACKWARD = "backward"
    FORWARD = "forward"


class Status(Enum):
    ERROR = "error"
    SUCCESS = "success"
