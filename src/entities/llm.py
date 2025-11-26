from msgspec import Struct

# model uri!
"gpt://<ВАШ_ИДЕНТИФИКАТОР_КАТАЛОГА>/yandexgpt-lite"


class CompletionOptions(Struct):
    stream: bool = False
    temperature: float = 0.6
    maxTokens: str = "2000"


class Message(Struct):
    text: str
    role: str = "user"


class LLMRequest(Struct):
    modelUri: str
    completionOptions: CompletionOptions
    messages: list[Message]
