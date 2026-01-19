import json
import time
from http import HTTPMethod
from logging import getLogger
from typing import Any, Self

import msgspec
from httpx import (
    AsyncClient,
    ConnectError,
    ConnectTimeout,
    Limits,
    ReadTimeout,
    RemoteProtocolError,
    Response,
)

from src.application.ports.http_client_port import HttpPort
from src.infrastructure.decorators import retry
from src.infrastructure.exceptions.network_exceptions import NetworkError

logger = getLogger(__name__)


class HTTPClient(HttpPort):
    def __init__(self, timeout: int | None = None) -> None:
        self.timeout = timeout
        self._client: AsyncClient | None = None

    async def __aenter__(self) -> Self:
        limits = Limits(
            max_connections=100,
            max_keepalive_connections=20,
            keepalive_expiry=30.0,
        )

        self._client = AsyncClient(timeout=self.timeout, limits=limits, http2=True)
        return self

    async def __aexit__(self, *args: Any) -> None:
        if self._client:
            await self._client.aclose()

    @retry(max_attempts=3, backoff=3.0)
    async def make_request(
        self,
        method: HTTPMethod = HTTPMethod.POST,
        url: str = "",
        headers: dict[str, str] | None = None,
        data: dict | str | bytes | None = None,
        params: dict | None = None,
        timeout: int | None = None,
        no_log_answer: bool = False,
    ) -> Response:
        """Performs an HTTP request to the API.

        Forms the full URL, performs the request with the specified parameters, and handles
        possible errors, logging information about them.

        Args:
            method: HTTP method from the list of allowed methods.
            url: Base URL.
            headers: HTTP request headers.
            data: Request body. Default is None.
            content_type: Content type: “json”, “form-data”, or None.
            no_log_answer: Do not log the response.
            params: Query parameters for the URL (used for GET requests).


        Returns:
            Response | None: The response object or None in case of an error.
        """
        if headers is None:
            headers: dict = {}
        start_time = time.time()

        try:
            logger.debug(
                f"{method} REQUEST to {url} {(p := f', params: {params}') if params else ''}"
            )
            if method == HTTPMethod.GET:
                params = params or {}
                response = await self._client.request(  # ty: ignore
                    method=method.value,
                    url=url,
                    headers=headers,
                    timeout=timeout if timeout else self.timeout,
                    params=params,
                )

            else:
                if isinstance(data, dict):
                    content = msgspec.json.encode(data)
                    if "Content-Type" not in headers:
                        headers = {**headers, "Content-Type": "application/json"}  # ty: ignore
                elif isinstance(data, str):
                    content = data.encode("utf-8")
                elif isinstance(data, bytes):
                    content = data
                else:
                    content = None
                response = await self._client.request(  # ty: ignore
                    method=method.value,
                    url=url,
                    headers=headers,
                    timeout=timeout if timeout else self.timeout,
                    content=content,
                )
            duration_ms = int((time.time() - start_time) * 1000)
            if no_log_answer:
                return response
            else:
                try:
                    logger.info(
                        {
                            "status_code": response.status_code,
                            "duration_ms": duration_ms,
                            "response": response.json(),
                        }
                    )
                except json.decoder.JSONDecodeError as e:
                    logger.warning(
                        {
                            "duration_ms": duration_ms,
                            "error": f"Failed to process the response for logging: {e}",
                            "response": str(response),
                        }
                    )
                return response

        except (ReadTimeout, ConnectTimeout, ConnectError, RemoteProtocolError) as error:
            logger.error(f"Connection failed: {type(error).__name__}")
            raise NetworkError(
                f"Connection failed: {type(error).__name__}", is_retryable=True
            ) from None

        except Exception as error:
            logger.exception(f"Unexpected HTTP error: {error}")
            raise

    async def close(self) -> None:
        await self._client.aclose()  # ty: ignore
