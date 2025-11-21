import datetime
from logging import getLogger

from src.clients.loki_client import LokiClient
from src.core.settings import settings
from src.entities.enums import LogLevel
from src.entities.loki import LogEntry
from src.responses.loki_responses import LogGroupByErrorType, LogsByErrorType, LokiQueryResult

logger = getLogger(__name__)


class LokiService:
    def __init__(self, loki_client: LokiClient) -> None:
        self.loki_client = loki_client
        self.app_name = settings.LOKI_APP_NAME

    async def get_recent_errors(self, hours: int = 1) -> LokiQueryResult:
        """Получает только ERROR логи за N часов"""
        logger.debug("Calling for get logs by level!")
        return await self.get_logs_by_level(LogLevel.ERROR, hours)

    async def get_logs_by_level(self, level: LogLevel, hours: int = 1) -> LokiQueryResult:
        query = f'{{level="{level.value}"}}'

        end_time = datetime.datetime.now()
        start_time = end_time - datetime.timedelta(hours=hours)

        logger.debug(f"Querying Loki with: {query}")
        logs = await self.loki_client.query_range(
            query=query, start_time=start_time, end_time=end_time
        )
        return logs

    async def group_errors_by_type(self, logs: LokiQueryResult) -> LogsByErrorType:
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

        # TODO: можно упростить и убрать лишние действия. например сделать через датаклассы или TypedDict
        groups = [
            LogGroupByErrorType(error=error_type, logs=log_list)
            for error_type, log_list in groups_dict.items()
        ]

        return LogsByErrorType(logs_groups=groups, total_count=len(groups))

    async def check_if_loki_is_ready(self) -> bool:
        logger.debug("Calling for loki client!")
        ready = await self.loki_client.is_loki_is_ready()
        return ready

    def _extract_error_type(self, message: str) -> str:
        # TODO: парсинг логов из стетхема, надо понять это и докинуть сервис а лучше переписать логику
        words = message.split()[:20]
        return " ".join(words)
