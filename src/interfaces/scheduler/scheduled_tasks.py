from logging import getLogger

import msgspec
from aiogram import Bot
from aiogram.fsm.storage.base import StorageKey
from aiogram.fsm.storage.redis import RedisStorage as AiogramRedisStorage
from aiogram.types import InlineKeyboardButton, InlineKeyboardMarkup
from apscheduler.schedulers.asyncio import AsyncIOScheduler
from apscheduler.triggers.interval import IntervalTrigger
from dishka import AsyncContainer

from src.application import AnalyzeLogsUseCase
from src.application.dto.analysis_report import AnalysisReport
from src.application.ports.notifier import Notifier
from src.domain import NotificationProvider, ReportType, TimeRange
from src.infrastructure.exceptions.base_exceptions import InfrastructureException
from src.infrastructure.llm.dto.session import LLMSession
from src.infrastructure.notifiers.telegram.telegram_notifier import TelegramNotifier
from src.infrastructure.services.conversation_manager import ConversationManager
from src.infrastructure.settings.app_settings import AppSettings
from src.infrastructure.settings.providers import NotificationSettings, TelegramConfig
from src.interfaces.bot.core.states import ScheduledSG
from src.interfaces.bot.formatters.html_formatter import ReportFormatter
from src.interfaces.bot.utils.messages import ask_llm_msg, no_errors_msg

logger = getLogger(__name__)


def get_scheduled_report_keyboard() -> InlineKeyboardMarkup:
    return InlineKeyboardMarkup(
        inline_keyboard=[
            [InlineKeyboardButton(text="Main menu", callback_data="main_menu")],
        ]
    )


def _get_notifier_type(notification_settings: NotificationSettings) -> type[Notifier]:
    match notification_settings.provider:
        case NotificationProvider.TELEGRAM:
            return TelegramNotifier


async def scheduled_analysis(container: AsyncContainer, is_initial: bool = False) -> None:
    try:
        use_case = await container.get(AnalyzeLogsUseCase)
        settings = await container.get(AppSettings)
        notifier_type = _get_notifier_type(settings.notification)
        notifier = await container.get(notifier_type)
        formatter = await container.get(ReportFormatter)
        bot = await container.get(Bot)
        fsm_storage = await container.get(AiogramRedisStorage)

        chat_id = settings.notification.get_config(TelegramConfig).chat_id
        if not chat_id:
            logger.error("chat_id not configured for scheduled reports!")
            return

        time_range = TimeRange(int(settings.schedule_interval_hours))

        report: AnalysisReport = await use_case.execute(time_range)

        if not report.has_errors:
            if is_initial:
                init_msg = (
                    "🚀 <b>Flarity Scheduler Started</b>\n\n"
                    f"{no_errors_msg(time_range)}\n\n"
                    f"📅 Next check: in {settings.schedule_interval_hours}h\n"
                    f"🔔 You'll be notified only when errors are found"
                )
                await notifier.send(init_msg)
                logger.info("Initial check: No errors found")
            else:
                logger.info("No errors found, skipping notification")
            return

        if report.messages:
            conv_manager = await container.get(ConversationManager)
            session = LLMSession()
            session.add_bulk_messages(report.messages)
            await conv_manager.save_session(str(chat_id), session)

        html = formatter.to_html(report, report_type=ReportType.ANALYZE)
        full_message = f"{html}\n\n{ask_llm_msg()}"

        await notifier.send(full_message, reply_markup=get_scheduled_report_keyboard())
        key = StorageKey(bot_id=bot.id, chat_id=int(chat_id), user_id=int(chat_id))
        await fsm_storage.set_state(key=key, state=ScheduledSG.asking_questions)

        data = {"report": msgspec.to_builtins(report)}
        await fsm_storage.set_data(key=key, data=data)

        logger.info(f"Scheduled report sent: {report.time_range.hour_and_unit}")

    except InfrastructureException as e:
        logger.exception(f"Analysis failed: {e.__class__.__name__}: {e}")
    except Exception as e:
        logger.exception(f"Unexpected error during analysis: {e}")


async def start_scheduler(container: AsyncContainer, settings: AppSettings) -> None:
    if not settings.schedule_enabled:
        return

    scheduler = AsyncIOScheduler()  # type: ignore[no-untyped-call]
    SCHEDULE_INTERVAL_HOURS = settings.schedule_interval_hours
    scheduler.add_job(  # type: ignore[no-untyped-call]
        scheduled_analysis,
        trigger=IntervalTrigger(hours=int(settings.schedule_interval_hours)),  # type: ignore[no-untyped-call]
        args=[container, False],
        id="log_analysis",
        max_instances=1,
        replace_existing=False,
    )
    scheduler.start()  # type: ignore[no-untyped-call]
    logger.info(f"Scheduler started. Will run every {SCHEDULE_INTERVAL_HOURS} hour/s.")
    logger.info("Running initial analysis...")

    try:
        await scheduled_analysis(container, is_initial=True)
    except Exception as e:
        logger.exception(f"Initial analysis failed: {e}")
