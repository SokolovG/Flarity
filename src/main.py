import asyncio
import logging
import sys

from apscheduler.schedulers.asyncio import AsyncIOScheduler
from apscheduler.triggers.interval import IntervalTrigger
from dishka import make_async_container

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


async def scheduled_analysis() -> None:
    container = make_async_container(MyProvider())

    try:
        service = await container.get(LogAnalysisService)
        await service.analyze_and_notify()
        logger.info("Analysis completed successfully")
    except BaseCustomException as e:
        logger.error(f"Analysis failed: {e.__class__.__name__}: {e}")
    except Exception as e:
        logger.exception(f"Unexpected error during analysis: {e}")
    finally:
        await container.close()


async def main() -> None:
    container = make_async_container(MyProvider())
    settings = await container.get(AppSettings)
    await container.close()

    SCHEDULE_INTERVAL_HOURS = settings.schedule_interval_hours

    scheduler = AsyncIOScheduler()
    scheduler.add_job(
        scheduled_analysis,
        trigger=IntervalTrigger(hours=int(SCHEDULE_INTERVAL_HOURS)),
        id="log_analysis",
        max_instances=1,
    )

    scheduler.start()
    logger.info(f"Scheduler started. Will run every {SCHEDULE_INTERVAL_HOURS} hour/s.")

    logger.info("Running initial analysis...")
    await scheduled_analysis()

    try:
        while True:
            await asyncio.sleep(3600)
    except (KeyboardInterrupt, SystemExit):
        logger.info("Shutting down scheduler...")
        scheduler.shutdown(wait=True)


if __name__ == "__main__":
    asyncio.run(main())
