from msgspec import Struct


class _OllamaMessage(Struct):
    role: str
    content: str


class OllamaResponse(Struct):
    model: str
    created_at: str
    message: _OllamaMessage
    done: bool
    total_duration: int | None = None
    prompt_eval_count: int | None = None
    eval_count: int | None = None


class OllamaErrorResponse(Struct):
    error: str
