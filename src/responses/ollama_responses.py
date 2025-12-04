from msgspec import Struct


class OllamaMessage(Struct):
    role: str
    content: str


class OllamaResponse(Struct):
    model: str
    created_at: str
    message: OllamaMessage
    done: bool

    done_reason: str | None = None
    total_duration: int | None = None
    load_duration: int | None = None
    prompt_eval_count: int | None = None
    prompt_eval_duration: int | None = None
    eval_count: int | None = None
    eval_duration: int | None = None


class OllamaErrorResponse(Struct):
    error: str
