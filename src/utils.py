from src.entities.loki import LogEntry


def format_logs_for_llm(logs: list[LogEntry]) -> str:
    string = ""
    for log in logs:
        string += log.message

    return string
