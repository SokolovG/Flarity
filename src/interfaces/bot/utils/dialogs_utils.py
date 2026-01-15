from typing import Any

from aiogram.types import Message
from aiogram_dialog import DialogManager


async def on_dialog_start(_: Any, manager: DialogManager) -> None:
    report = manager.start_data.get("report")  # type: ignore
    if report:
        manager.dialog_data["report"] = report

    return
