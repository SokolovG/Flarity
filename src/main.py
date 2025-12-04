import asyncio
import logging
import sys

from dishka import make_async_container

from src.core import MyProvider
from src.exceptions.base_exceptions import BaseCustomException
from src.services import LogAnalysisService

logging.basicConfig(
    level=logging.INFO,
    format="[%(levelname)s] %(name)s: %(message)s",
    handlers=[
        logging.StreamHandler(sys.stdout),
    ],
)
logging.getLogger("httpx").setLevel(logging.WARNING)
logging.getLogger("httpcore").setLevel(logging.WARNING)
logging.getLogger("asyncio").setLevel(logging.WARNING)
logging.getLogger("urllib3").setLevel(logging.WARNING)
logging.getLogger("src").setLevel(logging.DEBUG)

logger = logging.getLogger(__name__)


async def main() -> None:
    container = make_async_container(MyProvider())

    try:
        log_analyzer_service = await container.get(LogAnalysisService)

        ready = await log_analyzer_service.check_readiness()
        if not ready:
            logger.error("Services not ready!")
            sys.exit(1)

        await log_analyzer_service.analyze_and_notify()

    except BaseCustomException as e:
        logger.error(f"{e.__class__.__name__}: {e}")
        sys.exit(1)

    except Exception as e:
        logger.exception(f"Unexpected error: {e}")
        sys.exit(1)

    finally:
        await container.close()


if __name__ == "__main__":
    asyncio.run(main())
