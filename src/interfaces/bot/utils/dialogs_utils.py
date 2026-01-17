from typing import Any

from aiogram.types import Message
from aiogram_dialog import DialogManager, StartMode
from aiogram_dialog.widgets.input import MessageInput
from dishka.integrations.aiogram import FromDishka
from dishka.integrations.aiogram_dialog import inject

from src.infrastructure.llm.dto.session import LLMSession
from src.infrastructure.services.conversation_manager import ConversationManager
from src.interfaces.bot.core.constants import EASTER_EGGS_WORT_LIST
from src.interfaces.bot.core.states import MainSG
from src.interfaces.bot.utils.messages import unknown_command_msg


async def on_dialog_start(_: Any, manager: DialogManager) -> None:
    if not manager.start_data:
        return

    report = manager.start_data.get("report")  # type: ignore
    if report:
        manager.dialog_data["report"] = report

    return


@inject
async def on_analyze_dialog_start(
    _: Any,
    manager: DialogManager,
    conv_manager: FromDishka[ConversationManager],
) -> None:
    if not manager.start_data:
        return

    event = manager.event
    user_id = str(event.from_user.id)  # type: ignore[union-attr]

    report = manager.start_data.get("report")  # type: ignore[union-attr]
    if report:
        manager.dialog_data["report"] = report

    if report and report.get("messages"):
        session = LLMSession()
        session.add_bulk_messages(report["messages"])
        await conv_manager.save_session(user_id, session)


async def handle_unknown_text_in_dialog(
    message: Message, widget: MessageInput, manager: DialogManager
) -> None:
    if message.text in EASTER_EGGS_WORT_LIST:
        match message.text.lower():  # type: ignore[union-attr]
            case "ogonek":
                await message.answer("https://ogonek.app")
            case "author":
                await message.answer("https://github.com/SokolovG")
            case "how are you?":
                await message.answer("https://www.youtube.com/watch?v=afhOpXMllH0")
            case "shit":
                await message.answer("https://www.youtube.com/watch?v=qJrVo0OOtAE")
        return

    await message.answer(unknown_command_msg())
    await manager.start(MainSG.menu, mode=StartMode.RESET_STACK)
