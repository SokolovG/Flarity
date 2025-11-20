import asyncio

from dishka import make_async_container

from src.core import MyProvider
from src.services.log_analyzer_service import LogAnalysisService

container = make_async_container(MyProvider())
log_analyzer_service = container.get(LogAnalysisService)


async def main() -> None:
    while True:
        await log_analyzer_service.analyze_and_notify()  # type: ignore


if __name__ == "__main__":
    asyncio.run(main())
