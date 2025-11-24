from abc import ABC

from src.clients.http_client import HTTPClient
from src.core.settings import Settings


class BaseClient(ABC):
    def __init__(self, http_client: HTTPClient, settings: Settings) -> None:
        self._http = http_client
        self.settings = settings
