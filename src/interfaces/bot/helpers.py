from aiogram.types import CallbackQuery, Message

from src.application.ports.notifier import Notifier
from src.domain.entities.analysis_report import AnalysisReport
from src.domain.entities.enums import ReportType
from src.domain.utils import format_time_range
from src.domain.value_objects.time_range import TimeRange
from src.interfaces.bot.formatters.html_formatter import ReportFormatter
from src.interfaces.bot.keyboards import get_main_menu


async def handle_report_callback(
    callback: CallbackQuery,
    time_range: TimeRange,
    report: AnalysisReport,
    report_type: ReportType,
    formatter: ReportFormatter,
    notifier: Notifier,
    loading_msg: Message | None = None,
) -> None:
    if not report.has_errors:
        msg = None
        if loading_msg:
            msg = loading_msg
        else:
            msg = callback.message

        await msg.edit_text(
            f"✅ No errors found in {time_range.hours} {format_time_range(time_range)}"
        )
        return

    html = formatter.to_html(report, report_type)
    await notifier.send(html, chat_id=callback.message.chat.id)
    await callback.message.answer("Choose an action:", reply_markup=get_main_menu())
