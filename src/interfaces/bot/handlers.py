from aiogram.filters import Command, CommandStart
from aiogram.fsm.context import FSMContext
from aiogram.types import Message
from dishka.integrations.aiogram import FromDishka, inject

from src.application.ports.notifier import Notifier
from src.application.use_cases.analyze_logs_use_case import AnalyzeLogsUseCase
from src.application.use_cases.get_recent_errors_use_case import RecentErrorsUseCase
from src.application.use_cases.get_statistics_use_case import StatisticsLogsUseCase
from src.domain.entities.enums import ReportType
from src.domain.utils import format_time_range
from src.domain.value_objects.time_range import TimeRange
from src.infrastructure.constants import MAX_ERRORS_IN_ONE_REPORT
from src.infrastructure.settings.app_settings import AppSettings
from src.interfaces.bot import callbacks  # noqa: ignore
from src.interfaces.bot.entities import BotAction
from src.interfaces.bot.formatters.html_formatter import ReportFormatter
from src.interfaces.bot.formatters.text_formatter import BotTextFormatter
from src.interfaces.bot.keyboards import get_main_menu, get_period_options, get_yes_or_no_menu
from src.interfaces.bot.router import bot_router


@bot_router.message(CommandStart())
async def cmd_start(message: Message) -> None:
    await message.answer(
        "👋 Hello! I'm Flarity, a bot for analyzing logs.\nChoose an action below or use /help",
        reply_markup=get_main_menu(),
    )


@bot_router.message(Command("analyze"))
@inject
async def cmd_analyze(
    message: Message,
    use_case: FromDishka[AnalyzeLogsUseCase],
    notifier: FromDishka[Notifier],
    formatter: FromDishka[ReportFormatter],
) -> None:
    args = message.text.split()[1:] if message.text else []
    if not args:
        await message.answer(
            "Choose analysis period:", reply_markup=get_period_options(BotAction.ANALYZE)
        )
        return

    hours = int(args[0])
    time_range = TimeRange(hours)

    loading_msg = f"Analyzing logs for last {time_range.hours} {format_time_range(time_range)}\n{'This may take up to 30 seconds.'}"
    await message.answer(loading_msg)

    time_range = TimeRange(hours)
    report = await use_case.execute(time_range)

    if not report.has_errors:
        await message.answer(
            f"✅No errors found in {time_range.hours} {format_time_range(time_range)}"
        )
        return

    html = formatter.to_html(report, report_type=ReportType.ANALYZE)
    await notifier.send(
        html,
        chat_id=str(message.chat.id),
        reply_markup=get_yes_or_no_menu(action=BotAction.ANALYZE),
    )


@bot_router.message(Command("stats"))
@inject
async def cmd_stats(
    message: Message,
    use_case: FromDishka[StatisticsLogsUseCase],
    notifier: FromDishka[Notifier],
    formatter: FromDishka[ReportFormatter],
) -> None:
    args = message.text.split()[1:] if message.text else []

    if not args:
        await message.answer(
            "Choose analysis period:", reply_markup=get_period_options(BotAction.STATS)
        )
        return

    try:
        hours = int(args[0])

        time_range = TimeRange(hours)
        report = await use_case.execute(time_range)

        if not report.has_errors:
            await message.answer(
                f"✅No errors found in {time_range.hours} {format_time_range(time_range)}"
            )
            return

        html = formatter.to_html(report, report_type=ReportType.STATS)
        await notifier.send(html, chat_id=str(message.chat.id))
        await message.answer(text="Choose an action:", reply_markup=get_main_menu())

    except ValueError:
        await message.answer("❌ Invalid number! Use: <code>/stats 24</code>", parse_mode="HTML")


@bot_router.message(Command("recent"))
@inject
async def cmd_recent(
    message: Message,
    use_case: FromDishka[RecentErrorsUseCase],
    notifier: FromDishka[Notifier],
    formatter: FromDishka[ReportFormatter],
    state: FSMContext,
) -> None:
    args = message.text.split()[1:] if message.text else []

    if not args:
        await message.answer("Choose period:", reply_markup=get_period_options(BotAction.RECENT))
        return

    try:
        hours = int(args[0])

        time_range = TimeRange(hours)
        report = await use_case.execute(time_range)

        if not report.has_errors:
            await message.answer(
                f"✅ No errors found in {time_range.hours} {format_time_range(time_range)}"
            )
            return

        show_all_errors = None
        if len(report.logs) > MAX_ERRORS_IN_ONE_REPORT:  # type: ignore
            set_data = {"hours": hours}
            html = formatter.to_html(
                report, report_type=ReportType.RECENT, show_all_errors=show_all_errors
            )
            await notifier.send(html, chat_id=str(message.chat.id))
            msg = await message.answer(
                "Do you want see all errors?",
                reply_markup=get_yes_or_no_menu(action=BotAction.RECENT),
            )
            set_data["msg"] = msg
            await state.set_data(set_data)
            return

        html = formatter.to_html(
            report, report_type=ReportType.RECENT, show_all_errors=show_all_errors
        )
        await notifier.send(html, chat_id=str(message.chat.id))
        await message.answer(text="Choose an action:", reply_markup=get_main_menu())

    except ValueError:
        await message.answer(
            "❌ Invalid number! Use (example): <code>/recent 12</code>", parse_mode="HTML"
        )


@bot_router.message(Command("settings"))
@inject
async def cmd_settings(message: Message, app_settings: FromDishka[AppSettings]) -> None:
    info = BotTextFormatter.format_settings(
        provider=app_settings.llm_provider.provider,
        model=app_settings.llm.model,
        schedule_hourse=TimeRange(int(app_settings.schedule_interval_hours)),
        schedule_enabled=app_settings.schedule_enabled,
    )
    await message.answer(info, parse_mode="HTML")


@bot_router.message(Command("help"))
async def cmd_help(message: Message) -> None:
    help_text = BotTextFormatter.format_help()
    await message.answer(help_text, parse_mode="HTML", reply_markup=get_main_menu())


@bot_router.message()
async def easter_egg(message: Message) -> None:
    if message.text == "ogonek":
        await message.answer("https://ogonek.app")
