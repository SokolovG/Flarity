import asyncio
import logging
import sys

from aiogram import Bot, Dispatcher
from apscheduler.schedulers.asyncio import AsyncIOScheduler
from apscheduler.triggers.interval import IntervalTrigger
from dishka import AsyncContainer, make_async_container
from dishka.integrations.aiogram import AiogramProvider, setup_dishka

from src.core import MyProvider
from src.core.settings.app_settings import AppSettings
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


# def register_handlers(dispatcher: Dispatcher): ...


async def scheduled_analysis(container: AsyncContainer) -> None:
    try:
        service = await container.get(LogAnalysisService)
        await service.analyze_and_notify()
        logger.info("Analysis completed successfully")
    except BaseCustomException as e:
        logger.error(f"Analysis failed: {e.__class__.__name__}: {e}")
    except Exception as e:
        logger.exception(f"Unexpected error during analysis: {e}")


async def start_scheduler(container: AsyncContainer, settings: AppSettings) -> None:
    if not settings.schedule_enabled:
        return

    scheduler = AsyncIOScheduler()
    SCHEDULE_INTERVAL_HOURS = settings.schedule_interval_hours
    scheduler.add_job(
        scheduled_analysis,
        trigger=IntervalTrigger(hours=int(settings.schedule_interval_hours)),  # type: ignore
        args=[container],
        id="log_analysis",
        max_instances=1,
    )
    scheduler.start()
    logger.info(f"Scheduler started. Will run every {SCHEDULE_INTERVAL_HOURS} hour/s.")
    logger.info("Running initial analysis...")
    await scheduled_analysis(container)


async def main() -> None:
    container = make_async_container(MyProvider(), AiogramProvider())

    try:
        settings = await container.get(AppSettings)
        bot = await container.get(Bot)
        dp = await container.get(Dispatcher)

        setup_dishka(container, dp)
        # register_handlers(dp)

        tasks = []

        if settings.schedule_enabled:
            tasks.append(start_scheduler(container, settings))

        tasks.append(dp.start_polling(bot))

        await asyncio.gather(*tasks)

    except (KeyboardInterrupt, SystemExit):
        logger.info("Shutting down...")
    finally:
        await container.close()


if __name__ == "__main__":
    asyncio.run(main())
