from src.exceptions.base_exceptions import BaseCustomException


class TelegramError(BaseCustomException):
    """Базовая ошибка Telegram API"""


class TelegramRateLimitError(TelegramError):
    """429 Too Many Requests"""


class TelegramBadRequestError(TelegramError):
    """400 Bad Request"""
