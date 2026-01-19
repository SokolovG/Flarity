from logging import getLogger

import msgspec
from aiogram.types import CallbackQuery, Message
from aiogram_dialog import DialogManager
from aiogram_dialog.widgets.input import MessageInput
from aiogram_dialog.widgets.kbd import Button
from dishka.integrations.aiogram import FromDishka
from dishka.integrations.aiogram_dialog import inject

from src.application.use_cases.analyze_logs_use_case import AnalyzeLogsUseCase
from src.application.use_cases.ask_llm_use_case import AskLLMUseCase
from src.domain.exceptions import LLMChatLimitExceededError
from src.domain.value_objects.time_range import TimeRange
from src.infrastructure.llm.dto.session import LLMSession
from src.infrastructure.services.conversation_manager import ConversationManager
from src.interfaces.bot.core.states import AnalyzeSG, MainSG
from src.interfaces.bot.utils.error_handler import handle_bot_error
from src.interfaces.bot.utils.error_messages import BotErrorMessages
from src.interfaces.bot.utils.messages import (
    asking_llm_msg,
    loading_msg,
    no_errors_msg,
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
    load_msg = None
    try:
        await callback.answer()
        period = int(widget.widget_id.split("_")[1])
        time_range = TimeRange(period)
        load_msg = await callback.message.answer(  # ty:ignore[possibly-missing-attribute]
            loading_msg(time_range)
        )
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

        manager.dialog_data.update({"report": msgspec.to_builtins(report)})
        await manager.switch_to(AnalyzeSG.viewing_data)

    except Exception as e:
        await handle_bot_error(e, callback, manager, context="analyze_period")

    finally:
        if load_msg:
            try:
                await load_msg.delete()
            except Exception:
                pass


@inject
async def on_llm_question(
    message: Message,
    widget: MessageInput,
    manager: DialogManager,
    ask_use_case: FromDishka[AskLLMUseCase],
) -> None:
    load_msg = None
    try:
        load_msg = await message.answer(asking_llm_msg())

        if not message.text:
            await message.answer("Please send a text message.")
            return

        question: str = message.text
        user_id = str(message.from_user.id)  # ty:ignore[possibly-missing-attribute]

        llm_answer = await ask_use_case.execute(question, user_id)
        manager.dialog_data.update({"llm_answer": msgspec.to_builtins(llm_answer)})
        await manager.switch_to(AnalyzeSG.asking_questions)

    except LLMChatLimitExceededError as e:
        user_msg = BotErrorMessages.get_user_message(e)
        await message.answer(user_msg)
        await manager.done()
        await manager.start(MainSG.menu)

    except Exception as e:
        await handle_bot_error(e, message, manager, context="llm_question")

    finally:
        if load_msg:
            try:
                await load_msg.delete()
            except Exception:
                pass
