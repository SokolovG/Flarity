from aiogram import Bot, Dispatcher
from aiogram.types import BotCommand

from src.bot.router import bot_router


async def setup_bot(bot: Bot, dp: Dispatcher) -> None:
    dp.include_router(bot_router)
    commands = [
        BotCommand(command="start", description="Get started"),
        BotCommand(command="help", description="List of commands"),
        BotCommand(command="analyze", description="AI Analyze logs"),
        BotCommand(command="recent", description="Recent N errors"),
        BotCommand(command="stats", description="Statistics for the period"),
    ]
    await bot.set_my_commands(commands=commands)
