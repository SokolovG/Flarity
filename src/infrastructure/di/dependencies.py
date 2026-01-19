from typing import AsyncIterator

from aiogram import Bot, Dispatcher
from aiogram.fsm.storage.base import DefaultKeyBuilder
from aiogram.fsm.storage.redis import RedisStorage as AiogramRedisStorage
from dishka import Provider, Scope, provide
from redis.asyncio import Redis

from src.application import (
    AnalyzeLogsUseCase,
    AskLLMUseCase,
    RecentErrorsUseCase,
    StatisticsLogsUseCase,
)
from src.application.ports.llm_analyzer import LLMAnalyzer
from src.application.ports.log_source import LogSource
from src.application.ports.storage import Storage
from src.domain import ErrorGrouper, LLMProvider
from src.infrastructure.clients.http_client import HTTPClient
from src.infrastructure.clients.loki_client import LokiClient
from src.infrastructure.clients.telegram_client import TelegramClient
from src.infrastructure.llm.ollama.analyzer import OllamaAnalyzer
from src.infrastructure.llm.yandex.analyzer import YandexAnalyzer
from src.infrastructure.notifiers.telegram.telegram_notifier import TelegramNotifier
from src.infrastructure.rate_limiter import RateLimiter
from src.infrastructure.repositories.loki.loki_repository import LokiLogRepository
from src.infrastructure.services.conversation_manager import ConversationManager
from src.infrastructure.settings.app_settings import AppSettings
from src.infrastructure.settings.infrastructure import RedisConfig, ReportSettings, StorageSettings
from src.infrastructure.settings.providers import TelegramConfig
from src.infrastructure.storage.in_memory_storage import InMemoryStorage
from src.infrastructure.storage.redis_storage import RedisStorage
from src.interfaces.bot.formatters.html_formatter import ReportFormatter


class MyProvider(Provider):
    # ============================================================================
    # CORE SETTINGS & CONFIGURATION
    # ============================================================================

    @provide(scope=Scope.APP)
    def get_app_settings(self) -> AppSettings:
        return AppSettings()  # ty:ignore[missing-argument]

    @provide(scope=Scope.APP)
    def get_report_settings(self) -> ReportSettings:
        return ReportSettings()

    @provide(scope=Scope.APP)
    def get_storage_settings(self) -> StorageSettings:
        return StorageSettings()

    # ============================================================================
    # BOT & TELEGRAM INFRASTRUCTURE
    # ============================================================================

    @provide(scope=Scope.APP)
    def get_bot(self, settings: AppSettings) -> Bot:
        config = settings.notification.get_config(TelegramConfig)
        return Bot(token=config.bot_token)

    @provide(scope=Scope.APP)
    def get_dispatcher(self, aiogram_redis_storage: AiogramRedisStorage) -> Dispatcher:
        return Dispatcher(storage=aiogram_redis_storage)

    @provide(scope=Scope.APP)
    def get_telegram_client(self, http_client: HTTPClient, settings: AppSettings) -> TelegramClient:
        return TelegramClient(http_client, settings.notification)

    @provide(scope=Scope.APP)
    def get_telegram_notifier(
        self, telegram_client: TelegramClient, settings: AppSettings
    ) -> TelegramNotifier:
        return TelegramNotifier(telegram_client, settings.notification)

    @provide(scope=Scope.APP)
    def get_formatter(self, report_settings: ReportSettings) -> ReportFormatter:
        return ReportFormatter(report_settings)

    # ============================================================================
    # HTTP CLIENTS & EXTERNAL SERVICES
    # ============================================================================

    @provide(scope=Scope.APP)
    async def get_http_client(self) -> AsyncIterator[HTTPClient]:
        client = HTTPClient()
        async with client:
            yield client

    @provide(scope=Scope.APP)
    def get_loki_client(self, http_client: HTTPClient, settings: AppSettings) -> LokiClient:
        return LokiClient(http_client, settings.log_source)

    # ============================================================================
    # STORAGE & CACHING
    # ============================================================================

    @provide(scope=Scope.APP)
    async def get_redis_client(self, storage_settings: StorageSettings) -> AsyncIterator[Redis]:
        config = storage_settings.get_config(RedisConfig)

        client = Redis(
            host=config.host,
            port=config.port,
            db=config.db,
            password=config.password,
            decode_responses=True,
            max_connections=50,
            retry_on_timeout=True,
        )
        try:
            yield client
        finally:
            await client.aclose()

    @provide(scope=Scope.APP)
    def get_aiogram_fsm_storage(self, redis_client: Redis) -> AiogramRedisStorage:
        return AiogramRedisStorage(
            redis=redis_client, key_builder=DefaultKeyBuilder(with_destiny=True)
        )

    @provide(scope=Scope.APP)
    def get_session_storage(
        self,
        redis_client: Redis,
        storage_settings: StorageSettings,
    ) -> Storage:
        match storage_settings.provider:
            case "redis":
                return RedisStorage(redis_client)
            case "memory":
                return InMemoryStorage()
            case _:
                raise ValueError(f"Unknown provider: {storage_settings.provider}")

    @provide(scope=Scope.APP)
    def get_rate_limiter(self, storage: Storage) -> RateLimiter:
        return RateLimiter(storage)

    # ============================================================================
    # LLM & AI SERVICES
    # ============================================================================

    @provide(scope=Scope.APP)
    def get_llm_adapter(self, http_client: HTTPClient, settings: AppSettings) -> LLMAnalyzer:
        provider = LLMProvider(settings.llm_provider.provider)
        match provider:
            case LLMProvider.YANDEX:
                return YandexAnalyzer(http_client, settings)
            case LLMProvider.OLLAMA:
                return OllamaAnalyzer(http_client, settings)

    @provide(scope=Scope.APP)
    def get_conv_manager(self, storage: Storage) -> ConversationManager:
        return ConversationManager(storage)

    # ============================================================================
    # DOMAIN SERVICES
    # ============================================================================

    @provide(scope=Scope.APP)
    def get_error_grouper(self) -> ErrorGrouper:
        return ErrorGrouper()

    @provide(scope=Scope.APP)
    def get_log_source(self, loki_client: LokiClient) -> LogSource:
        return LokiLogRepository(loki_client)

    # ============================================================================
    # USE CASES
    # ============================================================================

    @provide(scope=Scope.APP)
    def get_analyze_logs_use_case(
        self,
        log_source: LogSource,
        llm_analyzer: LLMAnalyzer,
        error_grouper: ErrorGrouper,
        limiter: RateLimiter,
    ) -> AnalyzeLogsUseCase:
        return AnalyzeLogsUseCase(log_source, llm_analyzer, error_grouper, limiter)

    @provide(scope=Scope.APP)
    def get_ask_llm_use_case(
        self,
        llm_analyzer: LLMAnalyzer,
        conversation_manager: ConversationManager,
        limiter: RateLimiter,
    ) -> AskLLMUseCase:
        return AskLLMUseCase(llm_analyzer, conversation_manager, limiter)

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
