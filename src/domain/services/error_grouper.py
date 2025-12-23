from collections import defaultdict

from src.domain.entities.log_entry import LogEntry


class ErrorGrouper:
    def group_by_category(self, logs: list[LogEntry]) -> dict[str, list[LogEntry]]:
        groups = defaultdict(list)

        for log in logs:
            category = log.get_error_category()
            groups[category].append(log)

        return dict(groups)
