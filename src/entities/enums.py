from enum import Enum


class LLMProvider(Enum):
    GIGACHAT = "gigachat"
    LOCAL = "local"
    YANDEX = "yandex"


class LLMModel(Enum):
    YANDEX_GPT_LITE = "yandex-gpt-lite"
    YANDEX_GPT_PRO = "yandex-gpt-pro"


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
