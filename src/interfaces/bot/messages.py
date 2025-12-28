from src.domain.utils import format_time_range
from src.domain.value_objects.time_range import TimeRange
from src.interfaces.bot.entities import BotAction


def loading_msg(time_range: TimeRange) -> str:
    msg = f"Analyze logs for last {time_range.hours} {format_time_range(time_range)}\nThis may take up to 90 seconds."
    return msg


def choose_period_msg() -> str:
    msg = "Choose period:"
    return msg


def choose_an_action() -> str:
    msg = "Choose an action:"
    return msg


def failed_msg(error: BaseException, action: BotAction) -> str:
    msg = f"❌ {action.value.capitalize()} failed: {error}"
    return msg


def no_errors_msg(time_range: TimeRange) -> str:
    msg = f"✅ No errors found in {time_range.hours} {format_time_range(time_range)}"
    return msg


def ask_llm_msg() -> str:
    msg = "Do you want ask something from LLM about report?\nIf you want, write your question!"
    return msg
