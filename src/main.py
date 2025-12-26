import asyncio
import logging
import sys

from aiogram import Bot, Dispatcher
from apscheduler.schedulers.asyncio import AsyncIOScheduler
from apscheduler.triggers.interval import IntervalTrigger
from dishka import AsyncContainer, make_async_container
from dishka.integrations.aiogram import setup_dishka

from src.application.ports.notifier import Notifier
from src.dependencies import MyProvider
from src.domain.entities.enums import ReportType
from src.domain.utils import format_time_range
from src.domain.value_objects.time_range import TimeRange
from src.infrastructure.exceptions.base_exceptions import InfrastructureException
from src.infrastructure.settings.app_settings import AppSettings
from src.interfaces.bot import setup_bot
from src.interfaces.bot.formatters.html_formatter import ReportFormatter
from src.interfaces.bot.keyboards import get_main_menu

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


async def scheduled_analysis(container: AsyncContainer) -> None:
    try:
        from src.application.use_cases.analyze_logs_use_case import AnalyzeLogsUseCase

        use_case = await container.get(AnalyzeLogsUseCase)
        settings = await container.get(AppSettings)
        notifier = await container.get(Notifier)
        formatter = await container.get(ReportFormatter)
        report = await use_case.execute(TimeRange(int(settings.schedule_interval_hours)))

        if report.has_errors:
            html = formatter.to_html(report, report_type=ReportType.ANALYZE)
            await notifier.send(html, reply_markup=get_main_menu())
            logger.info(
                f"Scheduled report sent: {report.time_range.hours} {format_time_range(report.time_range)}"
            )
        else:
            logger.info(f"✅ No errors found, skipping notification")

    except InfrastructureException as e:
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
        trigger=IntervalTrigger(hours=int(settings.schedule_interval_hours)),
        args=[container],
        id="log_analysis",
        max_instances=1,
    )
    scheduler.start()
    logger.info(f"Scheduler started. Will run every {SCHEDULE_INTERVAL_HOURS} hour/s.")
    logger.info("Running initial analysis...")

    try:
        await scheduled_analysis(container)
    except Exception as e:
        logger.error(f"Initial analysis failed (non-critical): {e}")


async def main() -> None:
    container = make_async_container(MyProvider())

    try:
        settings = await container.get(AppSettings)
        bot = await container.get(Bot)
        dp = await container.get(Dispatcher)

        setup_dishka(container, dp)

        await setup_bot(bot, dp)

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
