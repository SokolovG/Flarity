from aiogram.types import CallbackQuery, InlineKeyboardMarkup

from src.application.dto.analysis_report import AnalysisReport
from src.application.dto.analysis_result import LLMAnalysisResult
from src.domain import ReportType, TimeRange
from src.infrastructure.dto import TelegramMessage
from src.infrastructure.notifiers.telegram_notifier import TelegramNotifier
from src.interfaces.bot.exceptions import BotParsingError
from src.interfaces.bot.formatters.html_formatter import ReportFormatter


class TelegramBotHelper:
    def __init__(self, formatter: ReportFormatter, notifier: TelegramNotifier):
        self.formatter = formatter
        self.notifier = notifier

    async def send_followup(
        self,
        text: str,
        chat_id: str,
        reply_markup: InlineKeyboardMarkup | None = None,
    ) -> None:
        await self.notifier.send(text, chat_id=chat_id, reply_markup=reply_markup)

    async def send_report(
        self,
        report: AnalysisReport,
        report_type: ReportType,
        chat_id: str,
        show_all_errors: bool = False,
        reply_markup: InlineKeyboardMarkup | None = None,
    ) -> TelegramMessage:
        html = self.formatter.to_html(report, report_type, show_all_errors)
        return await self.notifier.send(html, chat_id=chat_id, reply_markup=reply_markup)

    async def create_report(
        self,
        report: AnalysisReport,
        report_type: ReportType,
        show_all_errors: bool = False,
    ) -> str:
        return self.formatter.to_html(report, report_type, show_all_errors)

    async def send_llm_answer(
        self,
        answer: LLMAnalysisResult,
        chat_id: str,
    ) -> TelegramMessage:
        html = self.formatter.format_llm_answer(answer, ReportType.ANSWER)
        return await self.notifier.send(html, chat_id=chat_id)

    async def send_menu(
        self,
        chat_id: str,
        text: str,
        keyboard: InlineKeyboardMarkup,
    ) -> TelegramMessage:
        return await self.notifier.send(text, chat_id=chat_id, reply_markup=keyboard)

    def get_time_range_from_callback(self, callback: CallbackQuery) -> TimeRange:
        try:
            number = int(callback.data.split("_")[1])  # type: ignore
            return TimeRange(number)
        except (KeyError, ValueError, IndexError) as e:
            raise BotParsingError(f"Failed to parse callback data: {e}")
