from dishka import Provider, Scope, provide

from src.core.settings import Settings
from src.services.base_http_client import HTTPClient


class MyProvider(Provider):
    @provide(scope=Scope.APP)
    def get_settings(self) -> Settings:
        return Settings()

    @provide(scope=Scope.APP)
    def get_http_client(self) -> HTTPClient:
        return HTTPClient()
