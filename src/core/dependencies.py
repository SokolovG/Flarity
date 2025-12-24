from aiogram import Bot, Dispatcher
from dishka import Provider, Scope, provide

from src.application.ports.llm_analyzer import LLMAnalyzer
from src.application.ports.log_source import LogSource
from src.application.ports.notifier import Notifier
from src.application.use_cases.analyze_and_notify_use_case import AnalyzeLogsUseCase
from src.core.settings.app_settings import AppSettings
from src.infrastructure.clients.http_client import HTTPClient
from src.infrastructure.clients.loki_client import LokiClient
from src.infrastructure.clients.telegram_client import TelegramClient
from src.infrastructure.llm.ollama_analyzer import OllamaAnalyzer
from src.infrastructure.llm.providers import LLMProvider
from src.infrastructure.llm.yandex_analyzer import YandexAnalyzer
from src.infrastructure.notifiers.telegram_notifier import TelegramNotifier
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
    def get_log_analyzer_service(
        self,
        log_source_service: LogSource,
        notifier: Notifier,
        app_settings: AppSettings,
        fornatter: ReportFormatter,
    ) -> AnalyzeLogsUseCase:
        return AnalyzeLogsUseCase(
            log_source_service,
            notifier,
            app_settings,
            fornatter,
        )

    @provide(scope=Scope.APP)
    def get_llm_adapter(self, http_client: HTTPClient, settings: AppSettings) -> LLMAnalyzer:
        provider = LLMProvider(settings.llm_provider.provider)
        match provider:
            case LLMProvider.YANDEX:
                return YandexAnalyzer(http_client, settings)
            case LLMProvider.OLLAMA:
                return OllamaAnalyzer(http_client, settings)
