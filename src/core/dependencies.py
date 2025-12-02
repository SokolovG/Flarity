from dishka import Provider, Scope, provide

from src.clients import HTTPClient, LokiClient, TelegramClient
from src.core.settings.app_settings import AppSettings
from src.entities.enums import LLMProvider
from src.llm_adapters import BaseLLMAdapter, OllamaAdapter, YandexAdapter
from src.llm_adapters.ollama_adapter import OllamaAdapter
from src.services.base_services import LogSourceService
from src.services.llm_service import LLMService
from src.services.log_analyzer_service import LogAnalysisService
from src.services.loki_service import LokiService
from src.services.notification_service import NotificationService


class MyProvider(Provider):
    @provide(scope=Scope.APP)
    def get_app_settings(self) -> AppSettings:
        return AppSettings()

    @provide(scope=Scope.APP)
    def get_http_client(self) -> HTTPClient:
        return HTTPClient()

    @provide(scope=Scope.APP)
    def get_loki_client(self, http_client: HTTPClient, settings: AppSettings) -> LokiClient:
        return LokiClient(http_client=http_client, settings=settings.log_source)

    @provide(scope=Scope.APP)
    def get_log_source_service(
        self, loki_client: LokiClient, settings: AppSettings
    ) -> LogSourceService:
        return LokiService(loki_client=loki_client, settings=settings.log_source)

    @provide(scope=Scope.APP)
    def get_telegram_client(self, http_client: HTTPClient, settings: AppSettings) -> TelegramClient:
        return TelegramClient(http_client=http_client, settings=settings.notification)

    @provide(scope=Scope.APP)
    def get_notification_service(
        self, telegram_client: TelegramClient, settings: AppSettings
    ) -> NotificationService:
        return NotificationService(telegram_client=telegram_client, settings=settings.notification)

    @provide(scope=Scope.APP)
    def get_log_analyzer_service(
        self,
        log_source_service: LogSourceService,
        llm_service: LLMService,
        notification_service: NotificationService,
    ) -> LogAnalysisService:
        return LogAnalysisService(
            log_source_service=log_source_service,
            llm_service=llm_service,
            notification_service=notification_service,
        )

    @provide(scope=Scope.APP)
    def get_llm_service(self, llm_adapter: BaseLLMAdapter) -> LLMService:
        return LLMService(adapter=llm_adapter)

    @provide(scope=Scope.APP)
    def get_llm_adapter(self, http_client: HTTPClient, settings: AppSettings) -> BaseLLMAdapter:
        match settings.llm_provider.provider:
            case "yandex":
                return YandexAdapter(http_client, settings)
            case "ollama":
                return OllamaAdapter(http_client, settings)
