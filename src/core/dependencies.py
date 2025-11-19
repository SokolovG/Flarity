from dishka import Provider, Scope, provide

from src.clients.loki_client import LokiClient
from src.core.settings import Settings
from src.clients.http_client import HTTPClient


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
