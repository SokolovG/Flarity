from dishka import Provider, Scope, provide

from src.clients.http_client import HTTPClient
from src.clients.loki_client import LokiClient
from src.core.settings import Settings
from src.services.log_analyzer_service import LogAnalysisService
from src.services.loki_service import LokiService


class MyProvider(Provider):
    @provide(scope=Scope.APP)
    def get_settings(self) -> Settings:
        return Settings()

    @provide(scope=Scope.APP)
    def get_http_client(self) -> HTTPClient:
        return HTTPClient()

    @provide(scope=Scope.APP)
    def get_loki_client(self, http_client: HTTPClient) -> LokiClient:
        return LokiClient(http_client=http_client)

    @provide(scope=Scope.APP)
    def get_loki_service(self, loki_client: LokiClient) -> LokiService:
        return LokiService(loki_client=loki_client)

    @provide(scope=Scope.APP)
    def get_log_analyzer_service(self, loki_service: LokiService) -> LogAnalysisService:
        return LogAnalysisService(loki_service=loki_service)
