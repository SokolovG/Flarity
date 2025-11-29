from dishka import Provider, Scope, provide

from src.clients import HTTPClient, LokiClient
from src.core.settings import Settings
from src.entities.enums import LLMProvider
from src.llm_adapters import BaseLLMAdapter, LocalAdapter, YandexAdapter
from src.services import LLMService, LogAnalysisService, LokiService


class MyProvider(Provider):
    @provide(scope=Scope.APP)
    def get_settings(self) -> Settings:
        return Settings()

    @provide(scope=Scope.APP)
    def get_http_client(self) -> HTTPClient:
        return HTTPClient()

    @provide(scope=Scope.APP)
    def get_loki_client(self, http_client: HTTPClient, app_settings: Settings) -> LokiClient:
        return LokiClient(http_client=http_client, settings=app_settings)

    @provide(scope=Scope.APP)
    def get_loki_service(self, loki_client: LokiClient, app_settings: Settings) -> LokiService:
        return LokiService(loki_client=loki_client, settings=app_settings)

    @provide(scope=Scope.APP)
    def get_log_analyzer_service(
        self, loki_service: LokiService, llm_service: LLMService
    ) -> LogAnalysisService:
        return LogAnalysisService(loki_service=loki_service, llm_service=llm_service)

    @provide(scope=Scope.APP)
    def get_llm_service(self, llm_adapter: BaseLLMAdapter) -> LLMService:
        return LLMService(adapter=llm_adapter)

    @provide(scope=Scope.APP)
    def get_app_settings(self) -> Settings:
        return Settings()

    @provide(scope=Scope.APP)
    def get_llm_adapter(self, http_client: HTTPClient, settings: Settings) -> BaseLLMAdapter:
        match settings.LLMProvider:
            case LLMProvider.YANDEX:
                return YandexAdapter(http_client, settings)
            case LLMProvider.LOCAL:
                return LocalAdapter(http_client, settings)
