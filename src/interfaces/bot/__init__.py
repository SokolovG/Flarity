from aiogram import Bot, Dispatcher
from aiogram.types import BotCommand

from src.interfaces.bot import callbacks, handlers  # noqa: F401
from src.interfaces.bot.middleware.session_cleanup import SessionCleanupMiddleware
from src.interfaces.bot.router import bot_router


async def setup_bot(bot: Bot, dp: Dispatcher) -> None:
    dp.include_router(bot_router)
    dp.message.middleware(SessionCleanupMiddleware())
    commands = [
        BotCommand(command="start", description="Get started"),
        BotCommand(command="help", description="List of commands"),
        BotCommand(command="analyze", description="AI Analyze logs"),
        BotCommand(command="recent", description="Recent N errors"),
        BotCommand(command="stats", description="Statistics for the period"),
        BotCommand(command="settings", description="Settings of the app"),
        BotCommand(command="menu", description="main menu"),
    ]
    await bot.set_my_commands(commands)
