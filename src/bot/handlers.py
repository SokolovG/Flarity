from aiogram.filters import Command, CommandStart
from aiogram.types import Message
from dishka.integrations.aiogram import FromDishka, inject

from src.bot import callbacks  # noqa: F401
from src.bot.keyboards import get_analysis_options, get_main_menu
from src.bot.router import bot_router
from src.services import LogAnalysisService


@bot_router.message(CommandStart())
async def cmd_start(message: Message) -> None:
    await message.answer(
        "👋 Hello! I'm Flarity, a bot for analyzing logs.\nChoose an action below or use /help",
        reply_markup=get_main_menu(),
    )


@bot_router.message(Command("analyze"))
@inject
async def cmd_analyze(message: Message, service: FromDishka[LogAnalysisService]) -> None:
    args = message.text.split()[1:] if message.text else []
    if not args:
        await message.answer("Choose analysis period:", reply_markup=get_analysis_options())
        return

    hours = int(args[0])
    text = await service.analyze_logs(hours=hours)
    await message.answer(text, reply_markup=get_analysis_options())


@bot_router.message(Command("stats"))
@inject
async def cmd_stats(
    message: Message,
    service: FromDishka[LogAnalysisService],
) -> None:
    args = message.text.split()[1:] if message.text else []

    if not args:
        await message.answer("Choose analysis period:", reply_markup=get_analysis_options())
        return

    try:
        hours = int(args[0])
        if hours <= 0:
            await message.answer("❌ Hours must be positive!")
            return

        result = await service.get_statistics(hours=hours)
        await message.answer(result.report_html, parse_mode="HTML")

    except ValueError:
        await message.answer("❌ Invalid number! Use: <code>/stats 24</code>", parse_mode="HTML")


@bot_router.message(Command("recent"))
@inject
async def cmd_recent(
    message: Message,
    service: FromDishka[LogAnalysisService],
) -> None:
    args = message.text.split()[1:] if message.text else []

    if not args:
        await message.answer("Choose analysis period:", reply_markup=get_analysis_options())
        return

    try:
        hours = int(args[0])
        if hours <= 0:
            await message.answer("❌ Hours must be positive!")
            return

        result = await service.get_recent_errors(hours=hours)
        await message.answer(result.report_html, parse_mode="HTML")

    except ValueError:
        await message.answer("❌ Invalid number! Use: <code>/recent 12</code>", parse_mode="HTML")


@bot_router.message(Command("help"))
async def cmd_help(message: Message) -> None:
    help_text = """
        <b>Available commands:</b>

        /analyze [hours] - AI analysis of logs
        Example: <code>/analyze 6</code>

        /recent [hours] - Latest errors (without AI)
        Example: <code>/recent 1</code>

        /stats [hours] - Statistics summary
        Example: <code>/stats 24</code>

        /help - This help message
        """
    await message.answer(help_text, parse_mode="HTML")
