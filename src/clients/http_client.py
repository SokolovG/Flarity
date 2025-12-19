import json
import time
from http import HTTPMethod
from logging import getLogger

import msgspec
from httpx import AsyncClient, ConnectError, ConnectTimeout, ReadTimeout, Response

from src.core.decorators import retry
from src.exceptions.network_exeptions import NetworkError

logger = getLogger(__name__)


class HTTPClient:
    def __init__(self, default_timeout: int = 10) -> None:
        self.client = AsyncClient(timeout=default_timeout)

    @retry(max_attempts=3, backoff=1.0)
    async def make_request(
        self,
        headers: dict[str, str] = {},
        method: HTTPMethod = HTTPMethod.POST,
        url: str = "",
        data: dict | str | bytes | None = None,
        no_log_answer: bool = False,
        params: dict | None = None,
        timeout: int | None = 10,
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
        start_time = time.time()

        try:
            logger.info(
                f"{method} REQUEST to {url} {(p := f', params: {params}') if params else ''}"
            )
            if method == HTTPMethod.GET:
                params = params or {}
                response = await self.client.request(
                    method=method.value,
                    url=url,
                    headers=headers,
                    timeout=timeout,
                    params=params,
                )

            else:
                if isinstance(data, dict):
                    content = msgspec.json.encode(data)
                    if "Content-Type" not in headers:
                        headers = {**headers, "Content-Type": "application/json"}
                elif isinstance(data, str):
                    content = data.encode("utf-8")
                elif isinstance(data, bytes):
                    content = data
                else:
                    content = None
                response = await self.client.request(
                    method=method.value,
                    url=url,
                    headers=headers,
                    timeout=timeout,
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

        except (ReadTimeout, ConnectTimeout, ConnectError) as error:
            raise NetworkError(f"Connection failed: {error}", is_retryable=True) from error

        except Exception as error:
            logger.exception(f"Unexpected HTTP error: {error}")
            raise

    async def close(self) -> None:
        await self.client.aclose()
