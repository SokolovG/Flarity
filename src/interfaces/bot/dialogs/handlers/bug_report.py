from aiogram.types import Message
from aiogram_dialog import DialogManager
from aiogram_dialog.widgets.input import MessageInput
from dishka.integrations.aiogram import FromDishka
from dishka.integrations.aiogram_dialog import inject

from src.infrastructure.settings.app_settings import AppSettings
from src.infrastructure.settings.providers import TelegramConfig
from src.interfaces.bot.core.states import MainSG
from src.interfaces.bot.utils.error_handler import handle_bot_error
from src.interfaces.bot.utils.messages import report_been_sent_msg


@inject
async def on_bug_report(
    message: Message,
    widget: MessageInput,
    manager: DialogManager,
    settings: FromDishka[AppSettings],
) -> None:
    try:
        notification_settings = settings.notification
        settings_config = notification_settings.get_config(TelegramConfig)

        bug_text = message.text or message.caption or "No description"
        user_id = message.from_user.id  # ty: ignore
        username = message.from_user.username or "Unknown"  # ty: ignore
        bug_report_msg = f"Bug Report\nFrom: {user_id} (@{username})\nText: {bug_text}\nFile type: "
        if message.photo:
            photo = message.photo[-1]
            await message.bot.send_photo(  # ty: ignore
                chat_id=settings_config.chat_id_for_bug_report,
                photo=photo.file_id,
                caption=bug_report_msg + f"{message.content_type.value.capitalize()}",  # ty: ignore
            )

        elif message.video:
            await message.bot.send_video(  # ty: ignore
                chat_id=settings_config.chat_id_for_bug_report,
                video=message.video.file_id,
                caption=bug_report_msg + f"{message.content_type.value.capitalize()}",  # ty: ignore
            )
        elif message.document:
            mime_type = message.document.mime_type

            allowed_types = [
                "image/jpeg",
                "image/png",
                "image/gif",
                "image/webp",
                "application/pdf",
            ]

            if mime_type and mime_type in allowed_types:
                await message.bot.send_document(  # ty: ignore
                    chat_id=settings_config.chat_id_for_bug_report,
                    document=message.document.file_id,
                    caption=bug_report_msg,
                )
            else:
                await message.answer(
                    "⚠️ Unsupported file type!\n"
                    "Allowed: Photos, Videos, PDF\n\n"
                    "Please send your bug report again with a supported file."
                )
                return
        else:
            await message.bot.send_message(  # ty: ignore
                settings_config.chat_id_for_bug_report,
                bug_report_msg + f"{message.content_type.value.capitalize()}",  # ty: ignore
            )
        await message.answer(report_been_sent_msg())
        await manager.done()
        await manager.start(MainSG.menu)

    except Exception as e:
        await handle_bot_error(e, message, manager, context="bug_report")
