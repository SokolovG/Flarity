# src/interfaces/bot/utils/error_handler.py

from logging import getLogger
from typing import NoReturn

from aiogram.types import CallbackQuery, Message
from aiogram_dialog import DialogManager

from src.interfaces.bot.core.states import MainSG
from src.interfaces.bot.utils.error_messages import BotErrorMessages

logger = getLogger(__name__)


class BotErrorHandler:
    @staticmethod
    async def handle(
        e: Exception,
        event: Message | CallbackQuery,
        manager: DialogManager,
        context: str = "",
        *,
        redirect_to_menu: bool = True,
    ) -> None:
        """
        Handles the error: logs it, shows it to the user, redirects.

        Args:
            e: Exception
            event: Message or CallbackQuery
            manager: DialogManager
            context: Context for logs (operation name)
            redirect_to_menu: Whether to redirect to the main menu
        """
        log_msg = BotErrorMessages.get_log_message(e, context)
        log_level = getattr(e, "log_level", None)

        if log_level:
            logger.log(log_level, log_msg)
        else:
            logger.exception(log_msg)

        user_msg = BotErrorMessages.get_user_message(e)

        if isinstance(event, CallbackQuery):
            await event.answer()
            if event.message:
                await event.message.answer(user_msg)
        else:
            await event.answer(user_msg)

        if redirect_to_menu:
            await manager.done()
            await manager.start(MainSG.menu)


async def handle_bot_error(
    e: Exception,
    event: Message | CallbackQuery,
    manager: DialogManager,
    context: str = "",
    redirect: bool = True,
) -> None:
    await BotErrorHandler.handle(e, event, manager, context, redirect_to_menu=redirect)
