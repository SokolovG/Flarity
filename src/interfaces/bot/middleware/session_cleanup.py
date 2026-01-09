from collections.abc import Callable
from logging import getLogger
from typing import Any, Awaitable

from aiogram import BaseMiddleware
from aiogram.types import Update
from dishka import FromDishka

from src.application.services.conversation_manager import ConversationManager
from src.infrastructure.di.middleware_utils import aiogram_middleware_inject
from src.interfaces.bot.entities import BotStates

logger = getLogger(__name__)


class SessionCleanupMiddleware(BaseMiddleware):
    @aiogram_middleware_inject
    async def __call__(
        self,
        handler: Callable[[Update, dict[str, Any]], Awaitable[Any]],
        event: Update,
        data: dict[str, Any],
        conv_manager: FromDishka[ConversationManager],
    ) -> Any:
        state = data["state"]
        old_state = await state.get_state()
        result = await handler(event, data)
        new_state = await state.get_state()

        if old_state == BotStates.waiting_for_question and new_state != old_state:
            if event.message:
                user_id = str(event.message.from_user.id)  # type: ignore[union-attr]
                chat_id = event.message.chat.id
            elif event.callback_query:
                user_id = str(event.callback_query.from_user.id)
                chat_id = event.callback_query.message.chat.id  # type: ignore[union-attr]
            else:
                return result
            await conv_manager.clear_session(user_id)

            state_data = await state.get_data()
            report_msg_id = state_data.get("report_msg_id")

            if report_msg_id:
                bot = data.get("bot")

                if bot and chat_id:
                    try:
                        await bot.edit_message_reply_markup(
                            chat_id=chat_id,
                            message_id=report_msg_id,
                            reply_markup=None,
                        )
                    except Exception:
                        pass

            await state.set_data({})

        return result
