from logging import getLogger

from aiogram.types import CallbackQuery, Message
from aiogram_dialog import DialogManager
from aiogram_dialog.widgets.input import MessageInput
from aiogram_dialog.widgets.kbd import Button
from dishka.integrations.aiogram import FromDishka
from dishka.integrations.aiogram_dialog import inject

from src.application.use_cases.analyze_logs_use_case import AnalyzeLogsUseCase
from src.application.use_cases.ask_llm_use_case import AskLLMUseCase
from src.domain.value_objects.time_range import TimeRange
from src.infrastructure.llm.dto.session import LLMSession
from src.infrastructure.services.conversation_manager import ConversationManager
from src.interfaces.bot.core.constants import MAX_LLM_MESSAGES_IN_ONE_CHAT
from src.interfaces.bot.core.states import AnalyzeSG, MainSG
from src.interfaces.bot.utils.messages import (
    error_msg,
    llm_limit_chat_msg,
    loading_msg,
    no_errors_msg,
    operation_failed_msg,
)

logger = getLogger(__name__)


async def on_analyze(callback: CallbackQuery, widget: Button, manager: DialogManager) -> None:
    await manager.start(AnalyzeSG.period_selection)


@inject
async def on_analyze_period_click(
    callback: CallbackQuery,
    widget: Button,
    manager: DialogManager,
    use_case: FromDishka[AnalyzeLogsUseCase],
    conv_manager: FromDishka[ConversationManager],
) -> None:
    try:
        await callback.answer()
        period = int(widget.widget_id.split("_")[1])  # type: ignore
        time_range = TimeRange(period)
        load_msg = await callback.message.answer(loading_msg(time_range))  # type: ignore[union-attr]
        user_id = str(callback.from_user.id)

        report = await use_case.execute(time_range, user_id)

        if not report.has_errors:
            await load_msg.edit_text(no_errors_msg(time_range))
            await manager.done()
            await manager.start(MainSG.menu)
            return

        if report.messages:
            session = LLMSession()
            session.add_bulk_messages(report.messages)
            await conv_manager.save_session(user_id, session)

        await load_msg.delete()
        manager.dialog_data.update({"report": report})
        await manager.switch_to(AnalyzeSG.viewing_data)

    except Exception as e:
        logger.exception(operation_failed_msg(e))
        await callback.message.answer(error_msg())  # type: ignore[union-attr]
        await manager.done()
        await manager.start(MainSG.menu)


@inject
async def on_llm_question(
    message: Message,
    widget: MessageInput,
    manager: DialogManager,
    ask_use_case: FromDishka[AskLLMUseCase],
) -> None:
    try:
        question_count = manager.dialog_data.get("question_count", 0)
        if question_count >= MAX_LLM_MESSAGES_IN_ONE_CHAT:
            await message.answer(llm_limit_chat_msg(MAX_LLM_MESSAGES_IN_ONE_CHAT))
            await manager.done()
            await manager.start(MainSG.menu)

        question: str = message.text  # type: ignore
        user_id = str(message.from_user.id)  # type: ignore

        answer = await ask_use_case.execute(question, user_id)
        manager.dialog_data.update({"report": answer, "question_count": question_count + 1})
        await manager.switch_to(AnalyzeSG.asking_questions)

    except Exception as e:
        logger.exception(operation_failed_msg(e))
        await message.answer(error_msg())
        await manager.done()
        await manager.start(MainSG.menu)
