from abc import ABC, abstractmethod

from src.domain.entities.log_entry import LogEntry


class ErrorGroupingStrategy(ABC):
    @abstractmethod
    def extract_error_type(self, log: LogEntry) -> str: ...


class DefaultErrorGrouperStrategy(ErrorGroupingStrategy):
    def extract_error_type(self, log: LogEntry) -> str:
        if log.metadata.get("method") and log.metadata.get("uri"):
            uri_without_params = log.metadata.get("uri").split("?")[0]  # type: ignore
            return f"HTTP {log.metadata.get('uri')} {uri_without_params}"

        if log.metadata.get("target"):
            target_short = log.metadata.get("target").split("::")[-1]  # type: ignore
            message_prefix = log.message.split(":", 1)[0].strip()
            return f"{target_short}: {message_prefix}"

        return log.message.split(":", 1)[0].strip()[:50]


class ErrorGrouper:
    def __init__(self, strategy: ErrorGroupingStrategy | None = None):
        self.strategy = strategy or DefaultErrorGrouperStrategy()

    def group_by_category(self, logs: list[LogEntry]) -> dict[str, list[LogEntry]]:
        groups_dict: dict[str, list[LogEntry]] = {}

        for log in logs:
            error_type = self.strategy.extract_error_type(log)

            if error_type not in groups_dict:
                groups_dict[error_type] = []

            groups_dict[error_type].append(log)

        return groups_dict
