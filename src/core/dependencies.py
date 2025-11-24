from dishka import Provider, Scope, provide

from src.clients import HTTPClient, LLMClient, LokiClient
from src.core.settings import Settings
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
    def get_llm_client(self, http_client: HTTPClient, app_settings: Settings) -> LLMClient:
        return LLMClient(http_client=http_client, settings=app_settings)

    @provide(scope=Scope.APP)
    def get_llm_service(self, llm_client: LLMClient) -> LLMService:
        return LLMService(llm_client=llm_client)

    @provide(scope=Scope.APP)
    def get_app_settings(self) -> Settings:
        return Settings()
