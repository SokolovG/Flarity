import io

from aiogram.types import Message
from aiogram_dialog import DialogManager
from aiogram_dialog.widgets.input import MessageInput
from dishka.integrations.aiogram_dialog import inject

from src.interfaces.bot.constants import CHAT_ID_FOR_BUG_REPORT
from src.interfaces.bot.states import MainSG


@inject
async def on_bug_report(
    message: Message,
    widget: MessageInput,
    manager: DialogManager,
) -> None:
    bug_msg: str = message.text  # type: ignore
    # if message.content_type == "photo":
    # file_in_io = io.BytesIO()
    # TODO
    # file = await message.photo[-1].download(destination_file=file_in_io)

    await message.bot.send_message(
        CHAT_ID_FOR_BUG_REPORT,
        f"Bug Report\n"
        f"From: {message.from_user.id} (@{message.from_user.username})\n"
        f"Text: {message.text}",
    )
    await manager.done()
    await manager.start(MainSG.menu)
