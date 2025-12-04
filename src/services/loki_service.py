import datetime
import json
from logging import getLogger

from src.clients import LokiClient
from src.core.settings.log_source_settings import LogsSourceSettings
from src.entities.enums import LogLevel
from src.entities.loki import LogEntry
from src.responses import LogGroupByErrorType, LogsByErrorType, LogsSourceQueryResult
from src.services import LogSourceService

logger = getLogger(__name__)


class LokiService(LogSourceService):
    def __init__(self, loki_client: LokiClient, settings: LogsSourceSettings) -> None:
        super().__init__(settings)
        self.loki_client = loki_client

    async def get_recent_errors(self, hours: int) -> LogsSourceQueryResult:
        """Получает только ERROR логи за N часов"""
        logs = await self.get_logs_by_level(LogLevel.ERROR, hours)
        return logs

    async def get_logs_by_level(self, level: LogLevel, hours: int) -> LogsSourceQueryResult:
        query = f'{{level="{level.value}"}}'

        end_time = datetime.datetime.now()
        start_time = end_time - datetime.timedelta(hours=hours)

        logs = await self.loki_client.query_range(
            query=query, start_time=start_time, end_time=end_time
        )
        return logs

    async def group_errors_by_type(self, logs: LogsSourceQueryResult) -> LogsByErrorType:
        """
        Группирует ошибки по типу.

        ex:
        {
            "Database connection timeout": [log1, log2, log3],
            "API rate limit": [log4, log5],
        }
        """
        groups_dict: dict[str, list[LogEntry]] = {}
        for log in logs.logs:
            error_type = self._extract_error_type(log.message)

            if error_type not in groups_dict:
                groups_dict[error_type] = []

            groups_dict[error_type].append(log)

        groups = [
            LogGroupByErrorType(error=error_type, logs=log_list)
            for error_type, log_list in groups_dict.items()
        ]

        return LogsByErrorType(logs_groups=groups, total_count=len(groups))

    async def check_readiness(self) -> bool:
        ready = await self.loki_client.is_loki_is_ready()
        return ready

    def _extract_error_type(self, message: str) -> str:
        try:
            # TODO: получить формат логов, загнать его x
            log_data = json.loads(message)
            error_type: str = log_data.get("error_type", "UnknownError")
            return error_type

        except (json.JSONDecodeError, KeyError):
            words = message.split(":", 1)[0].strip()
            return words[:50]
