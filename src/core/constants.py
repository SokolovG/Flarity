from typing import Final

from httpx import ConnectError, ConnectTimeout, ReadTimeout

NETWORK_ERRORS: Final[tuple[type[Exception], ...]] = (ConnectTimeout, ReadTimeout, ConnectError)
