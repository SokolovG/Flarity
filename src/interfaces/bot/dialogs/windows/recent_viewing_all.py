from aiogram_dialog import Window
from aiogram_dialog.widgets.kbd import Cancel
from aiogram_dialog.widgets.text import Const, Format

from src.interfaces.bot.dialogs.getters.recent_getters import recent_all_getter
from src.interfaces.bot.states import RecentSG


def recent_viewing_all_window() -> Window:
    return Window(
        Format("{report_html_all}"),
        Cancel(Const("⬅️ Back to main menu")),
        state=RecentSG.viewing_all,
        getter=recent_all_getter,
    )
