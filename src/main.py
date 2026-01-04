import asyncio
import logging

from aiogram import Bot, Dispatcher
from dishka import make_async_container
from dishka.integrations.aiogram import setup_dishka

from src.infrastructure.di.dependencies import MyProvider
from src.infrastructure.logging.logging import setup_logging
from src.infrastructure.settings.app_settings import AppSettings
from src.interfaces.bot import setup_bot
from src.interfaces.scheduler.scheduled_tasks import start_scheduler

setup_logging(level="INFO")
logger = logging.getLogger(__name__)


async def main() -> None:
    container = make_async_container(MyProvider())

    try:
        settings = await container.get(AppSettings)
        bot = await container.get(Bot)
        dp = await container.get(Dispatcher)

        setup_dishka(container, dp)

        await setup_bot(bot, dp)

        tasks = []

        # TODO
        # if settings.schedule_enabled:
        #     tasks.append(start_scheduler(container, settings))

        tasks.append(dp.start_polling(bot))

        await asyncio.gather(*tasks)

    except (KeyboardInterrupt, SystemExit):
        logger.info("Shutting down...")
    finally:
        await container.close()


if __name__ == "__main__":
    asyncio.run(main())
