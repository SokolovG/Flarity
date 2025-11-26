from msgspec import Struct


class HTTPClientConfig(Struct):
    base_url: str
    timeout: int


class LokiConfig(Struct):
    base_url: str
    timeout: int


class TelegramConfig(Struct):
    base_url: str
    token: str
    timeout: int
