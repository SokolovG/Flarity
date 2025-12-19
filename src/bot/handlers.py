from aiogram import Bot, Dispatcher, Router
from aiogram.filters import Command, CommandStart
from aiogram.types import BotCommand, Message
from dishka.integrations.aiogram import FromDishka, inject

from src.services import LogAnalysisService

router = Router()


@router.message(CommandStart())
async def cmd_start(message: Message) -> None:
    await message.answer(
        "Hello! Im Flarity, I am a bot for analysing logs. Use /help to see all commands."
    )


@router.message(Command("analyze"))
@inject
async def cmd_analyze(message: Message, service: FromDishka[LogAnalysisService]) -> None:
    await service.analyze_and_notify()


@router.message(Command("help"))
async def cmd_help(message: Message) -> None:
    help_text = f"""
    <b>Commands:</b>

    /analyze [hours] - AI analysis of logs
    /last [n] - Latest errors
    /stats [hours] - Statistics
    /help - This help
    """
    await message.answer(help_text, parse_mode="HTML")


def register_handlers(dp: Dispatcher) -> None:
    dp.include_router(router)


async def set_bot_commands(bot: Bot) -> None:
    commands = [
        BotCommand(command="help", description="List of commands"),
        BotCommand(command="start", description="Get started"),
        BotCommand(command="analyze", description="AI Anylyze logs"),
        BotCommand(command="last", description="Last N errors"),
        BotCommand(command="stats", description="Statistics for the period"),
    ]
    await bot.set_my_commands(commands=commands)
