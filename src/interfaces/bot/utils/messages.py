from src.domain import TimeRange
from src.infrastructure import MAX_HOURS_IN_WEEK


def loading_msg(time_range: TimeRange) -> str:
    msg = f"Analyze logs for last {time_range.hour_and_unit}\nThis may take up to 90 seconds."
    return msg


# TODO: USE!
def choose_period_msg() -> str:
    msg = "Choose period:"
    return msg


def choose_an_action_msg() -> str:
    msg = "Choose an action:"
    return msg


def llm_limit_msg(limit: int) -> str:
    msg = f"Maximum {limit} questions reached. Please wait."
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


def asking_llm_msg() -> str:
    msg = "Asking LLM..."
    return msg


def greetings_msg() -> str:
    msg = "👋 Hello! I'm Flarity, a bot for analyzing logs.\nChoose an action below or use /help"
    return msg


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


def error_sending_bug_report() -> str:
    msg = "❌ Failed to send bug report."
    return msg
