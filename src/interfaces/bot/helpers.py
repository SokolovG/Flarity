from aiogram.types import CallbackQuery, InlineKeyboardMarkup, Message

from src.application.dto.analysis_report import AnalysisReport
from src.application.ports.notifier import Notifier
from src.application.use_cases.analyze_logs_use_case import AnalyzeLogsUseCase
from src.application.use_cases.get_recent_errors_use_case import RecentErrorsUseCase
from src.application.use_cases.get_statistics_use_case import StatisticsLogsUseCase
from src.domain.entities.enums import ReportType
from src.domain.value_objects.time_range import TimeRange
from src.interfaces.bot.exceptions import BotKeyError, BotValueError
from src.interfaces.bot.formatters.html_formatter import ReportFormatter
from src.interfaces.bot.keyboards import get_main_menu
from src.interfaces.bot.messages import no_errors_msg


class TelegramBotHelper:
    def __init__(self, formatter: ReportFormatter, notifier: Notifier):
        self.formatter = formatter
        self.notifier = notifier

    async def send_followup(
        self,
        text: str,
        chat_id: str,
        keyboard: InlineKeyboardMarkup | None = None,
    ) -> None:
        await self.notifier.send(text, chat_id=chat_id, reply_markup=keyboard)

    async def execute_report(
        self,
        use_case: AnalyzeLogsUseCase | RecentErrorsUseCase | StatisticsLogsUseCase,
        time_range: TimeRange,
        chat_id: str,
        report_type: ReportType,
        keyboard: InlineKeyboardMarkup | None = None,
        show_all_errors: bool | None = False,
    ) -> AnalysisReport | None:
        report = await use_case.execute(time_range)

        if not report.has_errors:
            await self._send_no_errors_message(chat_id, time_range)
            return None

        await self._format_and_send_report(
            report=report,
            report_type=report_type,
            chat_id=int(chat_id),
            show_all_errors=show_all_errors,
            keyboard=keyboard,
        )
        return report

    async def _send_no_errors_message(self, chat_id: str, time_range: TimeRange) -> None:
        text = no_errors_msg(time_range)
        await self.notifier.send(text, chat_id=chat_id, keyboard=get_main_menu())

    async def _format_and_send_report(
        self,
        report: AnalysisReport,
        report_type: ReportType,
        chat_id: int,
        show_all_errors: bool | None = False,
        keyboard: InlineKeyboardMarkup | None = None,
    ) -> None:
        html = self.formatter.to_html(report, report_type, show_all_errors)
        await self.notifier.send(html, chat_id=chat_id, keyboard=keyboard)

    def get_time_range_from_callback(self, callback: CallbackQuery) -> TimeRange:
        try:
            number = int(callback.data.split("_")[1])  # type: ignore
            return TimeRange(number)
        except KeyError:
            raise BotKeyError("Callback data can't be empty!")
        except Exception as e:
            raise BotValueError(f"Error: {e}")
