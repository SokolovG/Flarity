import json
import time
from http import HTTPMethod
from logging import getLogger

import msgspec
from httpx import AsyncClient, ConnectError, ConnectTimeout, ReadTimeout, Response

from src.core.decorators import retry

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
        """Выполняет HTTP-запрос к API.

        Формирует полный URL, выполняет запрос с заданными параметрами и обрабатывает
        возможные ошибки, логируя информацию о них.

        Args:
            method: HTTP-метод из списка разрешенных методов.
            url: Базовый урл
            headers: Заголовки HTTP-запроса.
            data: Тело запроса. По умолчанию None.
            content_type: content_type: Тип содержимого: "json", "form-data" или None.
            no_log_answer: Не выводить в логи ответ
            params: Query-параметры для URL (используется для GET-запросов)

        Returns:
            Response | None: Объект ответа или None в случае ошибки.
        """
        start_time = time.time()
        try:
            logger.info(f"{method} REQUEST to {url}, params: {params}")

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

        except (ReadTimeout, ConnectTimeout) as error:
            duration_ms = int((time.time() - start_time) * 1000)
            logger.error(
                {
                    "duration_ms": duration_ms,
                    "error": str(error),
                },
                exc_info=True,
            )
            raise

        except ConnectError as error:
            duration_ms = int((time.time() - start_time) * 1000)
            logger.error(
                {
                    "duration_ms": duration_ms,
                    "error": str(error),
                },
                exc_info=True,
            )
            raise

        except Exception as error:
            duration_ms = int((time.time() - start_time) * 1000)
            logger.error(
                {
                    "duration_ms": duration_ms,
                    "error": str(error),
                },
                exc_info=True,
            )
            raise

    async def close(self) -> None:
        await self.client.aclose()
