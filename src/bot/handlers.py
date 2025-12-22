from aiogram.filters import Command, CommandStart
from aiogram.types import Message
from dishka.integrations.aiogram import FromDishka, inject

from src.bot import callbacks  # noqa: F401
from src.bot.keyboards import get_analysis_options, get_main_menu
from src.bot.router import bot_router
from src.services import LogAnalysisService, LogSourceService


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
    print(args)
    if not args:
        await message.answer("Choose analysis period:", reply_markup=get_analysis_options())
        return

    hours = int(args[0])
    text = await service.analyze_logs(hours=hours)
    await message.answer(text, reply_markup=get_analysis_options())


@bot_router.message(Command("stats"))
async def cmd_stats(
    message: Message,
    log_source: FromDishka[LogSourceService],
) -> None: ...


@bot_router.message(Command("recent"))
async def cmd_recent(
    message: Message,
    log_source: FromDishka[LogSourceService],
) -> None: ...


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
