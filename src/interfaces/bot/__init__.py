from aiogram import Bot, Dispatcher
from aiogram.types import BotCommand

from src.interfaces.bot import handlers  # noqa: F401
from src.interfaces.bot.core.router import bot_router
from src.interfaces.bot.dialogs.dialogs import (
    analyze_dialog,
    bug_dialog,
    help_dialog,
    main_menu_dialog,
    recent_dialog,
    settings_dialog,
    stats_dialog,
)


async def setup_bot(bot: Bot, dp: Dispatcher) -> None:
    dp.include_router(main_menu_dialog)
    dp.include_router(analyze_dialog)
    dp.include_router(stats_dialog)
    dp.include_router(recent_dialog)
    dp.include_router(settings_dialog)
    dp.include_router(bug_dialog)
    dp.include_router(help_dialog)
    dp.include_router(bot_router)
    commands = [
        BotCommand(command="start", description="Get started"),
        BotCommand(command="help", description="List of commands"),
        BotCommand(command="analyze", description="AI Analyze logs"),
        BotCommand(command="recent", description="Recent N errors"),
        BotCommand(command="stats", description="Statistics for the period"),
        BotCommand(command="settings", description="Settings of the app"),
        BotCommand(command="menu", description="Main menu"),
        BotCommand(command="bug", description="Report a bug"),
    ]
    await bot.set_my_commands(commands)
