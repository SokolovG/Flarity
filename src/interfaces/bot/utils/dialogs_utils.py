from typing import Any

from aiogram_dialog import DialogManager
from dishka.integrations.aiogram import FromDishka
from dishka.integrations.aiogram_dialog import inject

from src.infrastructure.llm.dto.session import LLMSession
from src.infrastructure.services.conversation_manager import ConversationManager


async def on_dialog_start(_: Any, manager: DialogManager) -> None:
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
    event = manager.event
    user_id = str(event.from_user.id)  # type: ignore[union-attr]

    report = manager.start_data.get("report")  # type: ignore[union-attr]
    if report:
        manager.dialog_data["report"] = report

    if report and report.get("messages"):
        session = LLMSession()
        session.add_bulk_messages(report["messages"])
        await conv_manager.save_session(user_id, session)
