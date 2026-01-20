from abc import ABC, abstractmethod
from http import HTTPMethod
from typing import Any


class HttpPort(ABC):
    @abstractmethod
    async def make_request(
        self,
        method: HTTPMethod = HTTPMethod.POST,
        url: str = "",
        headers: dict[str, str] | None = None,
        data: dict | str | bytes | None = None,
        params: dict | None = None,
        timeout: int | None = None,
        no_log_answer: bool = False,
    ) -> Any: ...
