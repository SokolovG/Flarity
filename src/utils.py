from src.entities.loki import LogEntry


def format_logs_for_llm(logs: list[LogEntry]) -> str:
    string = ""
    for log in logs:
        str_log = f"[{log.timestamp.strftime('%Y-%m-%d %H:%M:%S')}] {log.level} {log.app} {log.message} \n"
        string += str_log

    return string
