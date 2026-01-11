from aiogram.types import Message
from aiogram_dialog import DialogManager
from aiogram_dialog.widgets.input import MessageInput

from src.interfaces.bot.core.constants import CHAT_ID_FOR_BUG_REPORT
from src.interfaces.bot.core.states import MainSG


async def on_bug_report(
    message: Message,
    widget: MessageInput,
    manager: DialogManager,
) -> None:
    bug_text = message.text or message.caption or "No description"
    user_id = message.from_user.id  # type: ignore[union-attr]
    username = message.from_user.username or "Unknown"  # type: ignore[union-attr]

    bug_report_msg = f"Bug Report\nFrom: {user_id} (@{username})\nText: {bug_text}"
    if message.photo:
        photo = message.photo[-1]
        await message.bot.send_photo(  # type: ignore[union-attr]
            chat_id=CHAT_ID_FOR_BUG_REPORT,
            photo=photo.file_id,
            caption=bug_report_msg,
        )

    else:
        await message.bot.send_message(  # type: ignore[union-attr]
            CHAT_ID_FOR_BUG_REPORT,
            bug_report_msg,
        )
    await manager.done()
    await manager.start(MainSG.menu)
