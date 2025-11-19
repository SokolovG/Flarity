from dataclasses import dataclass


@dataclass
class HTTPClientConfig:
    base_url: str
    timeout: int


@dataclass
class LokiConfig:
    base_url: str
    timeout: int


@dataclass
class TelegramConfig:
    base_url: str
    token: str
    timeout: int
