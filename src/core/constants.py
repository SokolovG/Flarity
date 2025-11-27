from typing import Final

from httpx import ConnectError, ConnectTimeout, ReadTimeout

NETWORK_ERRORS: Final[tuple[type[Exception], ...]] = (ConnectTimeout, ReadTimeout, ConnectError)

YANDEX_GPT_URl: Final[str] = "https://llm.api.cloud.yandex.net/foundationModels/v1/completion"
