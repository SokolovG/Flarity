from typing import Any

from aiogram_dialog import DialogManager

from src.interfaces.bot.utils.messages import report_been_sent, report_bug_msg


async def bug_getter(
    dialog_manager: DialogManager,
    **kwargs: Any,
) -> dict[str, str]:
    return {
        "report_bug": report_bug_msg(),
    }
