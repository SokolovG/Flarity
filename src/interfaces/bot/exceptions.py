class BaseTelegramBotException(Exception):
    """BAse error."""


class BotValueError(BaseTelegramBotException):
    """Analoge for ValueError."""


class BotKeyError(BaseTelegramBotException):
    """Analoge for ValueError."""
