from aiogram import Bot, Dispatcher
from dishka import Provider, Scope, provide

from src.clients import HTTPClient, LokiClient, TelegramClient
from src.core.settings.app_settings import AppSettings
from src.entities.enums import LLMProvider
from src.llm_adapters import BaseLLMAdapter, OllamaAdapter, YandexAdapter
from src.services import (
    LLMService,
    LogAnalysisService,
    LogSourceService,
    LokiService,
    NotificationService,
    ReportFormatter,
)


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
    def get_log_source_service(self, loki_client: LokiClient) -> LogSourceService:
        return LokiService(loki_client)

    @provide(scope=Scope.APP)
    def get_telegram_client(self, http_client: HTTPClient, settings: AppSettings) -> TelegramClient:
        return TelegramClient(http_client, settings.notification)

    @provide(scope=Scope.APP)
    def get_notification_service(
        self, telegram_client: TelegramClient, settings: AppSettings
    ) -> NotificationService:
        return NotificationService(telegram_client, settings.notification)

    @provide(scope=Scope.APP)
    def get_formatter(self) -> ReportFormatter:
        return ReportFormatter()

    @provide(scope=Scope.APP)
    def get_log_analyzer_service(
        self,
        log_source_service: LogSourceService,
        llm_service: LLMService,
        notification_service: NotificationService,
        app_settings: AppSettings,
        fornatter: ReportFormatter,
    ) -> LogAnalysisService:
        return LogAnalysisService(
            log_source_service,
            llm_service,
            notification_service,
            app_settings,
            fornatter,
        )

    @provide(scope=Scope.APP)
    def get_llm_service(self, llm_adapter: BaseLLMAdapter) -> LLMService:
        return LLMService(llm_adapter)

    @provide(scope=Scope.APP)
    def get_llm_adapter(self, http_client: HTTPClient, settings: AppSettings) -> BaseLLMAdapter:
        provider = LLMProvider(settings.llm_provider.provider)
        match provider:
            case LLMProvider.YANDEX:
                return YandexAdapter(http_client, settings)
            case LLMProvider.OLLAMA:
                return OllamaAdapter(http_client, settings)
