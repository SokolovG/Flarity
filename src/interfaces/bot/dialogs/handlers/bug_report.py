from aiogram.types import Message
from aiogram_dialog import DialogManager
from aiogram_dialog.widgets.input import MessageInput
from dishka.integrations.aiogram import FromDishka
from dishka.integrations.aiogram_dialog import inject

from src.infrastructure.settings.providers import NotificationSettings, TelegramConfig
from src.interfaces.bot.core.states import MainSG
from src.interfaces.bot.utils.messages import report_been_sent

# TODO: почистить type:ignore
# TODO: add loading msg llm


@inject
async def on_bug_report(
    message: Message,
    widget: MessageInput,
    manager: DialogManager,
    notification_settings: FromDishka[NotificationSettings],
) -> None:
    settings_config = notification_settings.get_config(TelegramConfig)

    bug_text = message.text or message.caption or "No description"
    user_id = message.from_user.id  # type: ignore[union-attr]
    username = message.from_user.username or "Unknown"  # type: ignore[union-attr]

    bug_report_msg = f"Bug Report\nFrom: {user_id} (@{username})\nText: {bug_text}"
    if message.photo:
        photo = message.photo[-1]
        await message.bot.send_photo(  # type: ignore[union-attr]
            chat_id=settings_config.chat_id_for_bug_report,
            photo=photo.file_id,
            caption=bug_report_msg,
        )

    else:
        await message.bot.send_message(  # type: ignore[union-attr]
            settings_config.chat_id_for_bug_report,
            bug_report_msg,
        )
    await message.answer(report_been_sent())
    await manager.done()
    await manager.start(MainSG.menu)
