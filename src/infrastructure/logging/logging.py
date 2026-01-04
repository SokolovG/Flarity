import logging
import sys


class ColoredFormatter(logging.Formatter):
    COLORS = {
        "DEBUG": "\033[36m",  # Cyan
        "INFO": "\033[32m",  # Green
        "WARNING": "\033[33m",  # Yellow
        "ERROR": "\033[31m",  # Red
        "CRITICAL": "\033[35m",  # Magenta
    }
    RESET = "\033[0m"

    def format(self, record: logging.LogRecord) -> str:
        record_path = ".".join(record.name.split(".")[1:])
        log_color = self.COLORS.get(record.levelname, self.RESET)
        record.levelname = f"{log_color}{record.levelname}{self.RESET}"
        record.name = f"\033[34m{record_path}{self.RESET}"
        return super().format(record)


class IgnoreNetworkTimeouts(logging.Filter):
    """Ignore ServerDisconnectedError from Telegram long polling"""

    def filter(self, record: logging.LogRecord) -> bool:
        message = record.getMessage()
        return not ("ServerDisconnectedError" in message and "Server disconnected" in message)


def setup_logging(level: str = "INFO") -> None:
    log_format = "%(asctime)s | %(levelname)-8s | %(name)s | %(message)s"
    date_format = "%Y-%m-%d %H:%M:%S"

    console_handler = logging.StreamHandler(sys.stdout)
    console_handler.setLevel(level)
    console_handler.setFormatter(ColoredFormatter(log_format, datefmt=date_format))

    file_handler = logging.FileHandler("flarity_logs.log", mode="w", encoding="utf-8")
    file_handler.setLevel(level)
    file_handler.setFormatter(logging.Formatter(log_format, datefmt=date_format))

    # handlers = [console_handler, file_handler]
    handlers = [console_handler]

    logging.basicConfig(level=level, handlers=handlers, force=True)
    logging.getLogger("httpx").setLevel(logging.WARNING)
    logging.getLogger("httpcore").setLevel(logging.WARNING)
    logging.getLogger("aiogram.event").setLevel(logging.WARNING)
    dispatcher_logger = logging.getLogger("aiogram.dispatcher")
    dispatcher_logger.setLevel(logging.WARNING)
    dispatcher_logger.addFilter(IgnoreNetworkTimeouts())


setup_logging(level="INFO")
