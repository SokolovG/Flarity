from enum import Enum


class LLMProvider(Enum):
    OLLAMA = "ollama"
    YANDEX = "yandex"


class LLMModel(Enum):
    YANDEX_GPT_LITE = ("yandexgpt-lite", LLMProvider.YANDEX)
    DEEPSEEK_R1_7B = ("deepseek-r1:7b", LLMProvider.OLLAMA)

    def __init__(self, value: tuple[str, LLMProvider], provider: LLMProvider):
        self._value_ = value
        self.provider = provider


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


class ReportType(Enum):
    ANALYZE = "analysis"
    RECENT = "recent"
    STATS = "stats"
    ANSWER = "answer"


class ReportTemplate(Enum):
    ANALYSIS_SHORT = "analysis_short.html"
    ANALYSIS_DETAILED = "analysis_detailed.html"
    RECENT_ERRORS = "recent_errors.html"
    STATISTICS = "statistics.html"
    ANSWER = "llm_answer.html"
