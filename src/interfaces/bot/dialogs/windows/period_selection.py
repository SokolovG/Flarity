from typing import Any

from aiogram.fsm.state import StatesGroup
from aiogram_dialog import Window
from aiogram_dialog.widgets.kbd import Back, Button, Column
from aiogram_dialog.widgets.text import Const

from src.interfaces.bot.constants import PERIODS
from src.interfaces.bot.messages import choose_period_msg


def period_selection_window(state_group: type[StatesGroup], on_click_handler: Any) -> Window:
    buttons = []
    for period in PERIODS:
        unit = "hour" if period == 1 else "hours"
        buttons.append(
            Button(Const(f"{period} {unit}"), id=f"period_{period}", on_click=on_click_handler)
        )

    buttons.append(Back(Const("⬅️ Back")))

    return Window(
        Const(choose_period_msg()),
        Column(*buttons),
        state=state_group.period_selection,  # type: ignore
    )
