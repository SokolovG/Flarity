from src.domain import TimeRange
from src.infrastructure import MAX_HOURS_IN_WEEK


def loading_msg(time_range: TimeRange) -> str:
    msg = f"Analyze logs for last {time_range.hour_and_unit}\nThis may take up to 90 seconds."
    return msg


def choose_period_msg() -> str:
    msg = "Choose period:"
    return msg


def choose_an_action_msg() -> str:
    msg = "Choose an action:"
    return msg


def llm_limit_chat_msg(limit: int) -> str:
    msg = (
        f"⚠️ You've reached the limit of {limit} questions per analysis.\n"
        "Start a new analysis to ask more questions."
    )
    return msg


def no_errors_msg(time_range: TimeRange) -> str:
    msg = f"✅ No errors found in {time_range.hour_and_unit}"
    return msg


def ask_llm_msg() -> str:
    msg = "Would you like to ask LLM anything about the report?\nIf you want, write your question!"
    return msg


def ask_llm_more_questions() -> str:
    msg = "You can ask more questions about this report, or write /menu to get back."
    return msg


def greetings_msg() -> str:
    msg = "👋 Hello! I'm Flarity, a bot for analyzing logs.\nChoose an action below or use /help"
    return msg


# TODO: add использование в хендлеры команды номера после команды /analyze 8.
def invalid_hour_range_msg() -> str:
    msg = f"❌ Hours must be between 1 and {MAX_HOURS_IN_WEEK}"
    return msg


def invalid_hour_format_msg() -> str:
    msg = "❌ Invalid number. Example: /analyze 6"
    return msg


def report_been_sent() -> str:
    msg = "✅ Thank you! The report has been sent."
    return msg


def report_bug_msg() -> str:
    msg = "Describe the problem in one message.\nYou can also add photo of bug."
    return msg


def error_msg() -> str:
    msg = "❌ Something went wrong. Try again."
    return msg


def operation_failed_msg(e: Exception) -> str:
    msg = f"Operation failed: {e}"
    return msg
