from aiogram_dialog import Window
from aiogram_dialog.widgets.kbd import Back, Button, Cancel
from aiogram_dialog.widgets.text import Const, Format

from src.interfaces.bot.dialogs.getters.recent_getters import recent_report_getter
from src.interfaces.bot.dialogs.handlers.recent_errors import on_show_all_errors
from src.interfaces.bot.states import RecentSG


def recent_viewing_report_window() -> Window:
    return Window(
        Format("{report_html}"),
        Button(
            Format("Show all {total_errors} errors"),
            id="show_all",
            on_click=on_show_all_errors,
            when="has_more_errors",
        ),
        Back(Const("⬅️ Back")),
        Cancel(Const("⬅️ To main menu")),
        state=RecentSG.viewing_data,
        getter=recent_report_getter,
    )
