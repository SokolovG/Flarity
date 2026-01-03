from logging import getLogger

from apscheduler.schedulers.asyncio import AsyncIOScheduler
from apscheduler.triggers.interval import IntervalTrigger
from dishka import AsyncContainer

from src.application.dto.analysis_report import AnalysisReport
from src.application.ports.notifier import Notifier
from src.application.use_cases.analyze_logs_use_case import AnalyzeLogsUseCase
from src.domain.entities.enums import NotificationProvider, ReportType
from src.domain.value_objects.time_range import TimeRange
from src.infrastructure.exceptions.base_exceptions import InfrastructureException
from src.infrastructure.notifiers.telegram_notifier import TelegramNotifier
from src.infrastructure.settings.app_settings import AppSettings
from src.infrastructure.settings.notification_settings import NotificationSettings
from src.interfaces.bot.formatters.html_formatter import ReportFormatter
from src.interfaces.bot.keyboards import get_main_menu

logger = getLogger(__name__)


def _get_notifier_type(notifcation_settings: NotificationSettings) -> type[Notifier]:
    match notifcation_settings.provider:
        case NotificationProvider.TELEGRAM:
            return TelegramNotifier


async def scheduled_analysis(container: AsyncContainer) -> None:
    try:
        use_case = await container.get(AnalyzeLogsUseCase)
        settings = await container.get(AppSettings)

        notifier_type = _get_notifier_type(settings.notification)
        notifier = await container.get(notifier_type)

        formatter = await container.get(ReportFormatter)
        report: AnalysisReport = await use_case.execute(
            TimeRange(int(settings.schedule_interval_hours))
        )

        if report.has_errors:
            html = formatter.to_html(report, report_type=ReportType.ANALYZE)
            await notifier.send(html, reply_markup=get_main_menu())
            logger.info(f"Scheduled report sent: {report.time_range.hour_and_unit}")
        else:
            logger.info(f"✅ No errors found, skipping notification")

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
        args=[container],
        id="log_analysis",
        max_instances=1,
    )
    scheduler.start()  # type: ignore[no-untyped-call]
    logger.info(f"Scheduler started. Will run every {SCHEDULE_INTERVAL_HOURS} hour/s.")
    logger.info("Running initial analysis...")

    try:
        await scheduled_analysis(container)
    except Exception as e:
        logger.exception(f"Initial analysis failed (non-critical): {e}")
