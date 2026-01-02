from src.domain.value_objects.time_range import TimeRange
from src.interfaces.bot.entities import BotAction


def loading_msg(time_range: TimeRange) -> str:
    msg = f"Analyze logs for last {time_range.hour_and_unit}\nThis may take up to 90 seconds."
    return msg


def choose_period_msg() -> str:
    msg = "Choose period:"
    return msg


def choose_an_action_msg() -> str:
    msg = "Choose an action:"
    return msg


def llm_limit_msg(limit: int) -> str:
    msg = f"Maximum {limit} questions reached. Returning to menu."
    return msg


def failed_msg(error: BaseException, action: BotAction) -> str:
    msg = f"❌ {action.value.capitalize()} failed: {error}"
    return msg


def no_errors_msg(time_range: TimeRange) -> str:
    msg = f"✅ No errors found in {time_range.hour_and_unit}"
    return msg


def ask_llm_msg() -> str:
    msg = "Do you want ask something from LLM about report?\nIf you want, write your question!"
    return msg


def ask_llm_one_more_time_msg() -> str:
    msg = "Ask another question or type /menu to return"
    return msg


def asking_llm_message() -> str:
    msg = "Asking LLM..."
    return msg


def greetings_msg() -> str:
    msg = "👋 Hello! I'm Flarity, a bot for analyzing logs.\nChoose an action below or use /help"
    return msg


def fail_hour_number() -> str:
    msg = "❌ Hours must be between 1 and 168"
    return msg


def fail_hour_parsing() -> str:
    msg = "❌ Invalid number. Example: /analyze 6"
    return msg
