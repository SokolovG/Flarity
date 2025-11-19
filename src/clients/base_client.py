from abc import ABC

from src.clients.http_client import HTTPClient


class BaseClient(ABC):
    def __init__(self, http_client: HTTPClient) -> None:
        self._http = http_client
