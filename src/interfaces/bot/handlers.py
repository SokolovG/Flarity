from logging import getLogger

from aiogram import F
from aiogram.filters import Command, CommandStart, StateFilter
from aiogram.fsm.context import FSMContext
from aiogram.types import CallbackQuery, Message
from aiogram_dialog import DialogManager, StartMode
from dishka.integrations.aiogram import FromDishka
from dishka.integrations.aiogram_dialog import inject

from src.application.use_cases.ask_llm_use_case import AskLLMUseCase
from src.domain.entities.enums import ReportType
from src.interfaces.bot.core.constants import EASTER_EGGS_WORT_LIST
from src.interfaces.bot.core.router import bot_router
from src.interfaces.bot.core.states import (
    AnalyzeSG,
    BugSG,
    HelpSG,
    MainSG,
    RecentSG,
    ScheduledSG,
    SettingsSG,
    StatsSG,
)
from src.interfaces.bot.formatters.html_formatter import ReportFormatter
from src.interfaces.bot.utils.messages import ask_llm_more_questions, error_msg

logger = getLogger(__name__)


@bot_router.message(CommandStart())
async def cmd_start(message: Message, dialog_manager: DialogManager) -> None:
    await dialog_manager.start(MainSG.menu, mode=StartMode.RESET_STACK)


@bot_router.message(Command("analyze"))
async def cmd_analyze(message: Message, dialog_manager: DialogManager) -> None:
    await dialog_manager.start(AnalyzeSG.period_selection, mode=StartMode.RESET_STACK)


@bot_router.message(Command("recent"))
async def cmd_recent(message: Message, dialog_manager: DialogManager) -> None:
    await dialog_manager.start(RecentSG.period_selection, mode=StartMode.RESET_STACK)


@bot_router.message(Command("stats"))
async def cmd_stats(message: Message, dialog_manager: DialogManager) -> None:
    await dialog_manager.start(StatsSG.period_selection, mode=StartMode.RESET_STACK)


@bot_router.message(Command("settings"))
async def cmd_settings(message: Message, dialog_manager: DialogManager) -> None:
    await dialog_manager.start(SettingsSG.viewing_data, mode=StartMode.RESET_STACK)


@bot_router.message(Command("bug"))
async def cmd_bug(message: Message, dialog_manager: DialogManager) -> None:
    await dialog_manager.start(BugSG.reporting, mode=StartMode.RESET_STACK)


@bot_router.message(Command("help"))
async def cmd_help(message: Message, dialog_manager: DialogManager) -> None:
    await dialog_manager.start(HelpSG.viewing_data, mode=StartMode.RESET_STACK)


@bot_router.message(Command("menu"))
async def cmd_menu(message: Message, dialog_manager: DialogManager) -> None:
    await dialog_manager.start(MainSG.menu, mode=StartMode.RESET_STACK)


@bot_router.message(StateFilter(None))
async def handle_unknown_message(message: Message, dialog_manager: DialogManager) -> None:
    if message.text in EASTER_EGGS_WORT_LIST:
        match message.text:
            case "ogonek":
                await message.answer("https://ogonek.app")
            case "author":
                await message.answer("https://github.com/SokolovG")

        return

    await message.answer("I don't understand you! Please use /help")
    await dialog_manager.start(MainSG.menu, mode=StartMode.RESET_STACK)


@bot_router.callback_query(F.data == "main_menu")
async def on_scheduled_menu(
    callback: CallbackQuery, dialog_manager: DialogManager, state: FSMContext
) -> None:
    await callback.answer()
    await state.clear()
    await dialog_manager.start(MainSG.menu, mode=StartMode.RESET_STACK)


@bot_router.message(StateFilter(ScheduledSG.asking_questions))
@inject
async def on_scheduled_llm_question(
    message: Message,
    state: FSMContext,
    ask_use_case: FromDishka[AskLLMUseCase],
    formatter: FromDishka[ReportFormatter],
) -> None:
    try:
        question: str = message.text  # type: ignore
        user_id = str(message.from_user.id)

        answer = await ask_use_case.execute(question, user_id)

        html = formatter.format_llm_answer(answer, ReportType.ANSWER)

        await message.answer(f"{html}\n\n{ask_llm_more_questions()}")

    except Exception as e:
        logger.exception(f"Failed to process LLM question: {e}")
        await message.answer(error_msg())
        await state.clear()
