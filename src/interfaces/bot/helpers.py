from aiogram.types import CallbackQuery, InlineKeyboardMarkup, Message

from src.application.dto.analysis_report import AnalysisReport
from src.application.ports.notifier import Notifier
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
    keyboard: InlineKeyboardMarkup | None = None,
    show_all_errors: bool = False,
    msg: str | None = None,
) -> dict:
    if not report.has_errors:
        msg_to_edit = loading_msg if loading_msg else callback.message
        await msg_to_edit.edit_text(
            f"✅ No errors found in {time_range.hours} {format_time_range(time_range)}",
            reply_markup=get_main_menu(),
        )
        return

    html = formatter.to_html(report, report_type, show_all_errors)
    msg_details = await notifier.send(
        html, chat_id=callback.message.chat.id, reply_markup=keyboard, return_message_details=True
    )

    if msg:
        await callback.message.answer(msg or "Choose an action:", reply_markup=get_main_menu())

    return msg_details
