from collections.abc import Callable
from logging import getLogger
from typing import Any, Awaitable

from aiogram import BaseMiddleware
from aiogram.types import TelegramObject
from dishka import FromDishka

from src.application.services.conversation_manager import ConversationManager
from src.infrastructure.di.middleware_utils import aiogram_middleware_inject
from src.interfaces.bot.entities import BotStates

logger = getLogger(__name__)


class SessionCleanupMiddleware(BaseMiddleware):
    @aiogram_middleware_inject
    async def __call__(
        self,
        handler: Callable[[TelegramObject, dict[str, Any]], Awaitable[Any]],
        event: TelegramObject,
        data: dict[str, Any],
        conv_manager: FromDishka[ConversationManager],
    ) -> Any:
        state = data["state"]
        old_state = await state.get_state()
        result = await handler(event, data)
        new_state = await state.get_state()

        if old_state == BotStates.waiting_for_question and new_state != old_state:
            user_id = str(event.from_user.id)  # type: ignore[attr-defined]
            await state.set_data({})
            await conv_manager.clear_session(user_id)

        return result
