from enum import Enum
from pathlib import Path
from typing import Final

TELEGRAM_MESSAGE_LIMIT: Final[int] = 4096
MAX_ERRORS_IN_ONE_REPORT: Final[int] = 10
MAX_SYMBOLS_LOG_MSG: Final[int] = 150
MAX_GROUPS_IN_REPORT: Final[int] = 5
MAX_RATE_LIMIT_CALLS: Final[int] = 1
MAX_RATE_LIMIT_PERIOD: Final[int] = 180
TTL_FOR_STORAGE: Final[int] = 600
BASE_DIR = Path(__file__).resolve().parent.parent.parent
LUA_INCR_AND_EXPIRE_SCRIPT: Final[str] = """
local current = redis.call('INCR', KEYS[1])
if current == 1 then
    redis.call('EXPIRE' KEYS[1], ARGV[1])
end
return current
"""


class TextType(str, Enum):
    HTML = "HTML"
    MARKDOWN = "MARKDOWN"
    PLAIN = "PLAIN"
