from collections.abc import Callable

from src.domain.exceptions import AnalysisFailedError, LLMChatLimitExceededError
from src.infrastructure.exceptions import (
    LLMAuthError,
    LLMError,
    LLMRateLimitError,
    LokiError,
    LokiUnavailableError,
    NetworkError,
    RateLimitExceeded,
    StorageError,
    TelegramError,
    TelegramRateLimitError,
)


class BotErrorMessages:
    _MESSAGES: dict[type[Exception], Callable[[Exception], str]] = {
        # User-caused errors (INFO level)
        RateLimitExceeded: lambda e: (
            f"⏳ Too many requests!\nPlease wait {e.details.get('ttl', 'a few')} seconds."
        ),
        LLMChatLimitExceededError: lambda e: (
            f"💬 You've reached the limit of {e.details.get('limit', 10)} questions.\n"
            f"Start a new analysis to continue."
        ),
        # Infrastructure errors (retryable, WARNING level)
        NetworkError: lambda e: "🌐 Network issue. Please try again in a moment.",
        LokiUnavailableError: lambda e: "📊 Log system temporarily unavailable. Try again later.",
        LLMRateLimitError: lambda e: "AI service rate limit. Please wait a bit.",
        TelegramRateLimitError: lambda e: "Too many messages. Slowing down...",
        StorageError: lambda e: "💾 Storage issue. Please try again.",
        # Configuration errors (ERROR level)
        LLMAuthError: lambda e: "🔑 AI authentication failed. Please contact admin.",
        # Generic fallbacks
        LokiError: lambda e: "📊 Error fetching logs. Try again later.",
        LLMError: lambda e: "AI service error. Please try again.",
        TelegramError: lambda e: "Messaging error. Please try again.",
        AnalysisFailedError: lambda e: f"⚠️ Analysis failed: {e.message}",
    }

    @classmethod
    def get_user_message(cls, e: Exception) -> str:
        if type(e) in cls._MESSAGES:
            return cls._MESSAGES[type(e)](e)

        for exc_type in type(e).__mro__:
            if exc_type in cls._MESSAGES:
                return cls._MESSAGES[exc_type](e)  # ty:ignore[invalid-argument-type]

        return "❌ Something went wrong. Please try again."

    @classmethod
    def get_log_message(cls, e: Exception, context: str = "") -> str:
        ctx = f" [{context}]" if context else ""
        return f"Operation failed{ctx}: {type(e).__name__}: {e}"
