from aiogram.types import CallbackQuery, InlineKeyboardMarkup, Message

from src.application.dto.analysis_report import AnalysisReport
from src.application.ports.notifier import Notifier
from src.domain.entities.enums import ReportType
from src.domain.utils import format_time_range
from src.domain.value_objects.time_range import TimeRange
from src.interfaces.bot.formatters.html_formatter import ReportFormatter
from src.interfaces.bot.keyboards import get_main_menu, get_yes_or_no_menu


async def handle_report_callback(
    callback: CallbackQuery,
    time_range: TimeRange,
    report: AnalysisReport,
    report_type: ReportType,
    formatter: ReportFormatter,
    notifier: Notifier,
    loading_msg: Message | None = None,
    keyboard: InlineKeyboardMarkup | None = get_main_menu(),
    show_all_errors: bool | None = False,
    msg: str | None = None,
) -> None:
    if not report.has_errors:
        msg = None
        if loading_msg:
            msg = loading_msg
        else:
            msg = callback.message

        await msg.edit_text(
            f"✅ No errors found in {time_range.hours} {format_time_range(time_range)}",
            reply_markup=get_main_menu(),
        )
        return
    html = formatter.to_html(report, report_type, show_all_errors)
    await notifier.send(html, chat_id=callback.message.chat.id)
    if not msg:
        msg = "Do you want ask something from LLM about report?\nIf you want, write your question!"
    await callback.message.answer(msg, reply_markup=keyboard)
