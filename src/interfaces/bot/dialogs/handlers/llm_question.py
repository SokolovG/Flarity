from aiogram.types import Message
from aiogram_dialog import DialogManager
from aiogram_dialog.widgets.input import MessageInput
from dishka.integrations.aiogram import FromDishka
from dishka.integrations.aiogram_dialog import inject

from src.application.use_cases.ask_llm_use_case import AskLLMUseCase


@inject
async def on_llm_question(
    message: Message,
    widget: MessageInput,
    manager: DialogManager,
    ask_use_case: FromDishka[AskLLMUseCase],
) -> None:
    question: str = message.text
    user_id = str(message.from_user.id)  # type: ignore

    answer = await ask_use_case.execute(question, user_id)
    await message.answer(answer.analysis_text)
