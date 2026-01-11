from aiogram_dialog import Window
from aiogram_dialog.widgets.kbd import Button
from aiogram_dialog.widgets.text import Const, Format

from src.interfaces.bot.dialogs.elements import on_cancel
from src.interfaces.bot.dialogs.getters.recent_getters import recent_all_getter
from src.interfaces.bot.states import RecentSG


def recent_viewing_all_window() -> Window:
    return Window(
        Format("{report_html_all}"),
        Button(Const("⬅️ Back"), id="cancel", on_click=on_cancel),
        state=RecentSG.viewing_all,
        getter=recent_all_getter,
    )
