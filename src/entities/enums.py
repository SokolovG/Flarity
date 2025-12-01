from enum import Enum


class LLMProvider(Enum):
    OLLAMA = "ollama"
    YANDEX = "yandex"


class LLMModel(Enum):
    YANDEX_GPT_LITE = "yandexgpt-lite"
    YANDEX_GPT_PRO_5_1 = "yandexgpt"
    YANDEX_GPT_5 = "yandexgpt"
    ALICE_LLM = "aliceai-llm"

    DEEPSEEK_R1_7B = "deepseek-r1:7b"
    DEEPSEEK_R1_8B = "deepseek-r1:8b"
    DEEPSEEK_R1_14B = "deepseek-r1:14b"

    QWEN3_CODER_7B = "qwen3-coder:7b"

    LLAMA_3_2 = "llama3.2"
    LLAMA_3_2_3B = "llama3.2:3b"
    MISTRAL = "mistral"
    GEMMA3_4B = "gemma3:4b"


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
