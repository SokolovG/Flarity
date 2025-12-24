from aiogram import Bot, Dispatcher
from dishka import Provider, Scope, provide

from src.application.ports.llm_analyzer import LLMAnalyzer
from src.application.ports.log_source import LogSource
from src.application.ports.notifier import Notifier
from src.application.use_cases.analyze_and_notify_use_case import AnalyzeLogsUseCase
from src.core.settings.app_settings import AppSettings
from src.domain.services.error_grouper import ErrorGrouper
from src.infrastructure.clients.http_client import HTTPClient
from src.infrastructure.clients.loki_client import LokiClient
from src.infrastructure.clients.telegram_client import TelegramClient
from src.infrastructure.llm.ollama_analyzer import OllamaAnalyzer
from src.infrastructure.llm.providers import LLMProvider
from src.infrastructure.llm.yandex_analyzer import YandexAnalyzer
from src.infrastructure.notifiers.telegram_notifier import TelegramNotifier
from src.infrastructure.repositories.loki_repository import LokiLogRepository
from src.interfaces.bot.formatters.html_formatter import ReportFormatter


class MyProvider(Provider):
    @provide(scope=Scope.APP)
    def get_bot(self, settings: AppSettings) -> Bot:
        return Bot(token=settings.notification.telegram_bot_token)

    @provide(scope=Scope.APP)
    def get_dispatcher(self) -> Dispatcher:
        return Dispatcher()

    @provide(scope=Scope.APP)
    def get_app_settings(self) -> AppSettings:
        return AppSettings()

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
    def get_formatter(self) -> ReportFormatter:
        return ReportFormatter()

    @provide(scope=Scope.APP)
    def get_analyze_logs_use_case(
        self,
        log_source: LogSource,
        llm_analyzer: LLMAnalyzer,
        error_grouper: ErrorGrouper,
        formatter: ReportFormatter,
        app_settings: AppSettings,
        notifier: Notifier,
    ) -> AnalyzeLogsUseCase:
        return AnalyzeLogsUseCase(
            log_source=log_source,
            notifier=notifier,
            app_settings=app_settings,
            llm=llm_analyzer,
            formatter=formatter,
            error_grouper=error_grouper,
        )

    @provide(scope=Scope.APP)
    def get_error_grouper(serf) -> ErrorGrouper:
        return ErrorGrouper()

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
