from msgspec import Struct


class OllamaErrorResponse(Struct):
    error: str


class OllamaResponse(Struct):
    model: str
    created_at: str
    response: str
    done: bool
    done_reason: str
    total_duration: int
    load_duration: int
    prompt_eval_count: int
    prompt_eval_duration: int
    eval_count: int
    eval_duration: int
