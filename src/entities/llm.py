from dataclasses import dataclass

# model uri!
"gpt://<ВАШ_ИДЕНТИФИКАТОР_КАТАЛОГА>/yandexgpt-lite"


@dataclass
class CompletionOptions:
    stream: bool = False
    temperature: float = 0.6
    maxTokens: str = "2000"


@dataclass
class Message:
    text: str
    role: str = "user"


@dataclass
class LLMRequest:
    modelUri: str
    completionOptions: CompletionOptions
    messages: Message
