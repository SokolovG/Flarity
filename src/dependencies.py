from typing import AsyncIterator

from aiogram import Bot, Dispatcher
from dishka import Provider, Scope, provide
from redis.asyncio import Redis

from src.application.ports.llm_analyzer import LLMAnalyzer
from src.application.ports.log_source import LogSource
from src.application.ports.notifier import Notifier
from src.application.ports.session_storage import SessionStorage
from src.application.services.conversation_manager import ConversationManager
from src.application.use_cases.analyze_logs_use_case import AnalyzeLogsUseCase
from src.application.use_cases.ask_llm_use_case import AskLLMUseCase
from src.application.use_cases.get_recent_errors_use_case import RecentErrorsUseCase
from src.application.use_cases.get_statistics_use_case import StatisticsLogsUseCase
from src.domain.entities.enums import LLMProvider
from src.domain.services.error_grouper import ErrorGrouper
from src.infrastructure.clients.http_client import HTTPClient
from src.infrastructure.clients.loki_client import LokiClient
from src.infrastructure.clients.telegram_client import TelegramClient
from src.infrastructure.llm.ollama.analyzer import OllamaAnalyzer
from src.infrastructure.llm.yandex.analyzer import YandexAnalyzer
from src.infrastructure.notifiers.telegram_notifier import TelegramNotifier
from src.infrastructure.repositories.loki_repository import LokiLogRepository
from src.infrastructure.settings.app_settings import AppSettings
from src.infrastructure.settings.notification_settings import TelegramConfig
from src.infrastructure.settings.report_settings import ReportSettings
from src.infrastructure.settings.storage_settings import RedisConfig, StorageSettings
from src.infrastructure.storage.in_memory_storage import InMemoryStorage
from src.infrastructure.storage.redis_storage import RedisStorage
from src.interfaces.bot.formatters.html_formatter import ReportFormatter
from src.interfaces.bot.helpers import TelegramBotHelper


class MyProvider(Provider):
    @provide(scope=Scope.APP)
    def get_bot(self, settings: AppSettings) -> Bot:
        config = settings.notification.get_config(TelegramConfig)
        return Bot(token=config.bot_token)

    @provide(scope=Scope.APP)
    def get_dispatcher(self) -> Dispatcher:
        return Dispatcher()

    @provide(scope=Scope.APP)
    def get_app_settings(self) -> AppSettings:
        return AppSettings()  # type: ignore[call-arg]

    @provide(scope=Scope.APP)
    def get_ask_llm_use_case(self, llm_analyzer: LLMAnalyzer) -> AskLLMUseCase:
        return AskLLMUseCase(llm_analyzer)

    @provide(scope=Scope.APP)
    def get_http_client(self) -> HTTPClient:
        return HTTPClient()

    @provide(scope=Scope.APP)
    def get_loki_client(self, http_client: HTTPClient, settings: AppSettings) -> LokiClient:
        return LokiClient(http_client, settings.log_source)

    @provide(scope=Scope.APP)
    def get_telegram_client(self, http_client: HTTPClient, settings: AppSettings) -> TelegramClient:
        return TelegramClient(http_client, settings.notification)

    @provide(scope=Scope.APP)
    def get_telegram_notifier(
        self, telegram_client: TelegramClient, settings: AppSettings
    ) -> TelegramNotifier:
        return TelegramNotifier(telegram_client, settings.notification)

    @provide(scope=Scope.APP)
    def get_report_settings(self) -> ReportSettings:
        return ReportSettings()

    @provide(scope=Scope.APP)
    def get_formatter(self, report_settings: ReportSettings) -> ReportFormatter:
        return ReportFormatter(report_settings)

    @provide(scope=Scope.APP)
    def get_telegram_bot_helper(
        self, formatter: ReportFormatter, notifier: TelegramNotifier
    ) -> TelegramBotHelper:
        return TelegramBotHelper(formatter, notifier)

    @provide(scope=Scope.APP)
    def get_storage_settings(self) -> StorageSettings:
        return StorageSettings()

    @provide(scope=Scope.APP)
    def get_conv_manager(self, storage: SessionStorage) -> ConversationManager:
        return ConversationManager(storage)

    @provide(scope=Scope.APP)
    async def get_redis_client(self, storage_settings: StorageSettings) -> AsyncIterator[Redis]:
        config = storage_settings.get_config(RedisConfig)

        client = Redis(
            host=config.host,
            port=config.port,
            db=config.db,
            password=config.password,
            decode_responses=True,
        )
        try:
            yield client
        finally:
            await client.aclose()

    @provide(scope=Scope.APP)
    def get_session_storage(
        self,
        redis_client: Redis,
        storage_settings: StorageSettings,
    ) -> SessionStorage:
        match storage_settings.provider:
            case "redis":
                return RedisStorage(redis_client)
            case "memory":
                return InMemoryStorage()
            case _:
                raise ValueError(f"Unknown provider: {storage_settings.provider}")

    @provide(scope=Scope.APP)
    def get_analyze_logs_use_case(
        self, log_source: LogSource, llm_analyzer: LLMAnalyzer, error_grouper: ErrorGrouper
    ) -> AnalyzeLogsUseCase:
        return AnalyzeLogsUseCase(
            log_source,
            llm_analyzer,
            error_grouper,
        )

    @provide(scope=Scope.APP)
    def get_stats_logs_use_case(
        self,
        log_source: LogSource,
        llm_analyzer: LLMAnalyzer,
        error_grouper: ErrorGrouper,
    ) -> StatisticsLogsUseCase:
        return StatisticsLogsUseCase(
            log_source,
            llm_analyzer,
            error_grouper,
        )

    @provide(scope=Scope.APP)
    def get_recent_logs_use_case(
        self,
        log_source: LogSource,
        llm_analyzer: LLMAnalyzer,
    ) -> RecentErrorsUseCase:
        return RecentErrorsUseCase(log_source, llm_analyzer)

    @provide(scope=Scope.APP)
    def get_error_grouper(self) -> ErrorGrouper:
        return ErrorGrouper()

    @provide(scope=Scope.APP)
    def get_log_source(self, loki_client: LokiClient) -> LogSource:
        return LokiLogRepository(loki_client)

    @provide(scope=Scope.APP)
    def get_llm_adapter(self, http_client: HTTPClient, settings: AppSettings) -> LLMAnalyzer:
        provider = LLMProvider(settings.llm_provider.provider)
        match provider:
            case LLMProvider.YANDEX:
                return YandexAnalyzer(http_client, settings)
            case LLMProvider.OLLAMA:
                return OllamaAnalyzer(http_client, settings)
