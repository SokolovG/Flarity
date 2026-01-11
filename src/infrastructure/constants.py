from enum import Enum
from pathlib import Path
from typing import Final

# Schedule settings
SCHEDULE_INTERVAL_HOURS: Final[int] = 6

# Rate limiting settings
RATE_LIMIT_ANALYZE_CALLS: Final[int] = 3
RATE_LIMIT_ASK_LLM_CALLS: Final[int] = 10
RATE_LIMIT_ANALYZE_PERIOD: Final[int] = 180  # seconds
RATE_LIMIT_ASK_LLM_PERIOD: Final[int] = 300  # seconds
RATE_LIMITER_ANALYZE_PREFIX: Final[str] = "analyze_rate_limit:"
RATE_LIMITER_ASK_LLM_PREFIX: Final[str] = "ask_llm_rate_limit:"
# Telegram limits
TELEGRAM_MESSAGE_LIMIT: Final[int] = 4096  # Telegram API limit for message length

# Report display limits
MAX_SYMBOLS_LOG_MSG: Final[int] = 150
MAX_GROUPS_IN_REPORT: Final[int] = 5

# Storage settings
TTL_FOR_STORAGE: Final[int] = 3600  # 1 hour in seconds
LLM_SESSION_PREFIX: Final[str] = "llm:session:"

# Time limits
MAX_HOURS_IN_WEEK: Final[int] = 168  # 7 days * 24 hours

# LLM processing timeout
LLM_PROCESSING_TIMEOUT_SECONDS: Final[int] = 90

# Template validation
MIN_TEMPLATE_OUTPUT_LENGTH: Final[int] = 10
BASE_DIR = Path(__file__).resolve().parent.parent.parent
LUA_INCR_AND_EXPIRE_SCRIPT: Final[str] = """
local current = redis.call('INCR', KEYS[1])
if current == 1 then
    redis.call('EXPIRE', KEYS[1], ARGV[1])
end
return current
"""


class TextType(str, Enum):
    HTML = "HTML"
    MARKDOWN = "MARKDOWN"
    PLAIN = "PLAIN"
