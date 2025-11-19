from enum import Enum


class LLMProvider(Enum):
    GIGACHAT = "gigachat"
    LOCAL = "local"
    YANDEX_GPT = "yandex_gpt"


class LogLevel(Enum):
    INFO = "info"
    WARNING = "warning"
    ERROR = "error"
    CRITICAL = "critical"


class Directions(Enum):
    BACKWARD = "backward"
    FORWARD = "forward"
