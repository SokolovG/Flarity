from aiogram.fsm.context import FSMContext
from aiogram.types import CallbackQuery, InlineKeyboardMarkup, Message

from src.application.dto.analysis_report import AnalysisReport
from src.application.dto.analysis_result import LLMAnalysisResult
from src.domain import ReportType, TimeRange
from src.infrastructure.constants import MAX_HOURS_IN_WEEK
from src.infrastructure.dto import TelegramMessage
from src.infrastructure.notifiers.telegram_notifier import TelegramNotifier
from src.interfaces.bot.entities import BotAction, BotStates
from src.interfaces.bot.exceptions import BotParsingError
from src.interfaces.bot.formatters.html_formatter import ReportFormatter
from src.interfaces.bot.keyboards import get_main_menu, get_period_options
from src.interfaces.bot.messages import (
    choose_period_msg,
    invalid_hour_format_msg,
    invalid_hour_range_msg,
    no_errors_msg,
)


class TelegramBotHelper:
    def __init__(self, formatter: ReportFormatter, notifier: TelegramNotifier):
        self.formatter = formatter
        self.notifier = notifier

    async def get_time_range_from_msg(
        self, message: Message, action: BotAction, state: FSMContext
    ) -> TimeRange | None:
        try:
            args = message.text.split()[1:] if message.text else []
            if not args:
                await message.answer(
                    text=choose_period_msg(), reply_markup=get_period_options(action)
                )
                await state.set_state(BotStates.period_selection)
                return None

            hours = int(args[0])
            if hours <= 0 or hours > MAX_HOURS_IN_WEEK:
                await message.answer(invalid_hour_range_msg())
                return None
            return TimeRange(hours)

        except ValueError:
            await message.answer(invalid_hour_format_msg())
            return None

    async def send_followup(
        self,
        text: str,
        chat_id: str,
        reply_markup: InlineKeyboardMarkup | None = None,
    ) -> None:
        await self.notifier.send(text, chat_id=chat_id, reply_markup=reply_markup)

    async def send_no_errors_message(self, chat_id: str, time_range: TimeRange) -> None:
        text = no_errors_msg(time_range)
        await self.notifier.send(text, chat_id=chat_id, reply_markup=get_main_menu())

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
