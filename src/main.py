import asyncio
from logging import getLogger

from dishka import make_async_container

from src.core import MyProvider
from src.services.log_analyzer_service import LogAnalysisService

logger = getLogger(__name__)


async def main() -> None:
    container = make_async_container(MyProvider())

    try:
        log_analyzer_service = await container.get(LogAnalysisService)
        ready = await log_analyzer_service.check_readiness()
        logger.debug(f"Services is ready - it is {ready}")

        while True:
            await log_analyzer_service.analyze_and_notify()
    finally:
        await container.close()


if __name__ == "__main__":
    asyncio.run(main())
