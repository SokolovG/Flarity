from aiogram.filters import Command, CommandStart
from aiogram.types import Message
from dishka.integrations.aiogram import FromDishka, inject

from src.bot import callbacks  # noqa: F401
from src.bot.keyboards import (
    get_analysis_options,
    get_main_menu,
    get_recent_options,
)
from src.bot.router import bot_router
from src.core.settings.app_settings import AppSettings
from src.core.utils import format_hours, get_help_text_for_bot, get_settings_for_bot
from src.services import LogAnalysisService
from src.services.notification_service import NotificationService


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
    service: FromDishka[LogAnalysisService],
    notifier: FromDishka[NotificationService],
) -> None:
    args = message.text.split()[1:] if message.text else []
    if not args:
        await message.answer("Choose analysis period:", reply_markup=get_analysis_options())
        return

    hours = int(args[0])

    loading_msg = f"Analyzing logs for last {hours} {format_hours(hours)}\n{'This may take up to 30 seconds.'}"
    await message.answer(loading_msg)
    result = await service.analyze_logs(hours)
    await notifier.send_message(result.report_html, chat_id=str(message.chat.id))
    await message.answer(reply_markup=get_main_menu())


@bot_router.message(Command("stats"))
@inject
async def cmd_stats(
    message: Message,
    service: FromDishka[LogAnalysisService],
    notifier: FromDishka[NotificationService],
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

        result = await service.get_statistics(hours)
        await notifier.send_message(result.report_html, chat_id=str(message.chat.id))
        await message.answer(reply_markup=get_main_menu())

    except ValueError:
        await message.answer("❌ Invalid number! Use: <code>/stats 24</code>", parse_mode="HTML")


@bot_router.message(Command("recent"))
@inject
async def cmd_recent(
    message: Message,
    service: FromDishka[LogAnalysisService],
    notifier: FromDishka[NotificationService],
) -> None:
    args = message.text.split()[1:] if message.text else []

    if not args:
        await message.answer("Choose period:", reply_markup=get_recent_options())
        return

    try:
        hours = int(args[0])
        if hours <= 0:
            await message.answer("❌ Hours must be positive!")
            return

        result = await service.get_recent_errors(hours)
        await notifier.send_message(result.report_html, chat_id=str(message.chat.id))
        await message.answer(reply_markup=get_main_menu())

    except ValueError:
        await message.answer("❌ Invalid number! Use: <code>/recent 12</code>", parse_mode="HTML")


@bot_router.message(Command("settings"))
@inject
async def cmd_settings(message: Message, app_settings: FromDishka[AppSettings]) -> None:
    info = get_settings_for_bot(
        provider=app_settings.llm_provider.provider,
        model=app_settings.llm.model,
        schedule_hourse=app_settings.schedule_interval_hours,
        schedule_enabled=app_settings.schedule_enabled,
    )
    await message.answer(info, parse_mode="HTML")


@bot_router.message(Command("help"))
async def cmd_help(message: Message) -> None:
    help_text = get_help_text_for_bot()
    await message.answer(help_text, parse_mode="HTML", reply_markup=get_main_menu())
