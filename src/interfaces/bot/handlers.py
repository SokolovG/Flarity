from logging import getLogger

from aiogram.filters import Command, CommandStart
from aiogram.types import Message
from aiogram_dialog import DialogManager

from src.interfaces.bot.router import bot_router
from src.interfaces.bot.states import (
    AnalyzeSG,
    BugSG,
    HelpSG,
    MainSG,
    RecentSG,
    SettingsSG,
    StatsSG,
)

logger = getLogger(__name__)


@bot_router.message(CommandStart())
async def cmd_start(message: Message, dialog_manager: DialogManager) -> None:
    await dialog_manager.start(MainSG.menu)


@bot_router.message(Command("analyze"))
async def cmd_analyze(message: Message, dialog_manager: DialogManager) -> None:
    await dialog_manager.start(AnalyzeSG.period_selection)


@bot_router.message(Command("stats"))
async def cmd_stats(message: Message, dialog_manager: DialogManager) -> None:
    await dialog_manager.start(StatsSG.period_selection)


@bot_router.message(Command("recent"))
async def cmd_stats(message: Message, dialog_manager: DialogManager) -> None:
    await dialog_manager.start(RecentSG.period_selection)


@bot_router.message(Command("settings"))
async def cmd_stats(message: Message, dialog_manager: DialogManager) -> None:
    await dialog_manager.start(SettingsSG.viewing_data)


@bot_router.message(Command("bug"))
async def cmd_bug(message: Message, dialog_manager: DialogManager) -> None:
    await dialog_manager.start(BugSG.viewing_instructions)


@bot_router.message(Command("help"))
async def cmd_help(message: Message, dialog_manager: DialogManager) -> None:
    await dialog_manager.start(HelpSG.viewing_data)


@bot_router.message(Command("menu"))
async def cmd_menu(message: Message, dialog_manager: DialogManager) -> None:
    await dialog_manager.start(MainSG.menu)


# TODO: единый формат логирования и ошибок в тг
# @bot_router.message(BotStates.waiting_for_question)
# @inject
# async def handle_llm_question(
#     message: Message,
#     ask_use_case: FromDishka[AskLLMUseCase],
#     helper: FromDishka[TelegramBotHelper],
#     state: FSMContext,
# ) -> None:
#     data = await state.get_data()
#     report_msg_id = data.get("report_msg_id")

#     if report_msg_id:
#         try:
#             await message.bot.edit_message_reply_markup(
#                 chat_id=message.chat.id, message_id=report_msg_id, reply_markup=None
#             )
#         except Exception:
#             pass

#     question_count = data.get("question_count", 0)

#     if question_count >= MAX_LLM_MESSAGES_IN_ONE_CHAT:
#         await message.answer(
#             text=llm_limit_msg(MAX_LLM_MESSAGES_IN_ONE_CHAT), reply_markup=get_main_menu()
#         )
#         await state.set_state(BotStates.main_menu)
#         await state.set_data({})
#         return

#     if message.text == "/menu":
#         await message.answer(choose_an_action_msg(), reply_markup=get_main_menu())
#         await state.set_state(BotStates.main_menu)
#         return

#     question = message.text
#     if not question:
#         return

#     chat_id = str(message.chat.id)
#     user_id = str(message.from_user.id)

#     loading_msg = await message.answer(text=asking_llm_msg())

#     try:
#         answer: LLMAnalysisResult = await ask_use_case.execute(question, user_id)

#         await helper.send_llm_answer(answer, chat_id)
#         await loading_msg.delete()

#         await helper.send_menu(chat_id, ask_llm_one_more_time_msg(), get_back_to_menu_button())
#         await state.update_data(question_count=question_count + 1)
#         await state.set_state(BotStates.waiting_for_question)

#     except Exception as e:
#         if not isinstance(e, InfrastructureException):
#             logger.exception(e)
#         else:
#             logger.error(e)
#         await loading_msg.delete()
#         await message.answer(failed_msg(e, BotAction.ASK), reply_markup=get_main_menu())


# @bot_router.message(Command(BotAction.BUG.value))
# async def cmd_bug(message: Message, state: FSMContext) -> None:
#     await state.set_state(BotStates.reporting_bug)
#     await message.answer("Describe the problem in one message. Or send /cancel to cancel.")


# @bot_router.message(BotStates.reporting_bug)
# async def handle_bug_report(message: Message, state: FSMContext) -> None:
#     if message.text == "/cancel":
#         await state.set_state(BotStates.main_menu)
#         await message.answer("Cancelled", reply_markup=get_main_menu())
#         return

#     try:
#         await message.bot.send_message(
#             CHAT_ID_FOR_BUG_REPORT,
#             f"Bug Report\n"
#             f"From: {message.from_user.id} (@{message.from_user.username})\n"
#             f"Text: {message.text}",
#         )

#         await message.answer(report_been_sent(), reply_markup=get_main_menu())
#     except Exception as e:
#         logger.error(f"Failed to send bug report: {e}")
#         await message.answer(error_sending_bug_report())

#     await state.set_state(BotStates.main_menu)


# @bot_router.message()
# async def handle_unknown_message(message: Message, state: FSMContext) -> None:
#     if message.text in EASTER_EGGS_WORT_LIST:
#         await state.set_state(BotStates.viewing_data)
#         match message.text:
#             case "ogonek":
#                 await message.answer("https://ogonek.app")
#             case "author":
#                 await message.answer("https://github.com/SokolovG")
#     else:
#         await message.answer("I don't understand you! Please use /help")
