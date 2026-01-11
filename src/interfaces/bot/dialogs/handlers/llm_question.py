from aiogram.types import Message
from aiogram_dialog import DialogManager
from aiogram_dialog.widgets.input import MessageInput
from dishka.integrations.aiogram import FromDishka
from dishka.integrations.aiogram_dialog import inject

from src.application.use_cases.ask_llm_use_case import AskLLMUseCase
from src.infrastructure.exceptions.rate_limit_exceptions import RateLimitExceeded
from src.interfaces.bot.constants import MAX_LLM_MESSAGES_IN_ONE_CHAT
from src.interfaces.bot.states import AnalyzeSG, MainSG
from src.interfaces.bot.utils.messages import llm_limit_msg


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
            await message.answer(text=llm_limit_msg(MAX_LLM_MESSAGES_IN_ONE_CHAT))
            await manager.done()
            await manager.switch_to(MainSG.menu)

        question: str = message.text  # type: ignore
        user_id = str(message.from_user.id)  # type: ignore

        answer = await ask_use_case.execute(question, user_id)
        manager.dialog_data.update({"report": answer, "question_count": question_count + 1})
        await manager.switch_to(AnalyzeSG.asking_questions)

    except Exception as e:
        manager.dialog_data.update({"report": e})
        await manager.done()
        await manager.switch_to(MainSG.menu)
