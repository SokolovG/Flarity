from src.domain.entities.log_entry import LogEntry


class ErrorGrouper:
    groups_dict: dict[str, list[LogEntry]] = {}

    def group_by_category(self, logs: list[LogEntry]) -> dict[str, list[LogEntry]]:
        groups_dict: dict[str, list[LogEntry]] = {}

        for log in logs:
            error_type = self._extract_error_type(log)

            if error_type not in groups_dict:
                groups_dict[error_type] = []

            groups_dict[error_type].append(log)

        return groups_dict

    def _extract_error_type(self, log: LogEntry) -> str:
        if log.method and log.uri:
            uri_without_params = log.uri.split("?")[0]
            return f"HTTP {log.method} {uri_without_params}"

        if log.target:
            target_short = log.target.split("::")[-1]
            message_prefix = log.message.split(":", 1)[0].strip()
            return f"{target_short}: {message_prefix}"

        return log.message.split(":", 1)[0].strip()[:50]
