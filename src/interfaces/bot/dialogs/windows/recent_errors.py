from aiogram_dialog import Window
from aiogram_dialog.widgets.kbd import Back, Button
from aiogram_dialog.widgets.text import Const, Format

from src.interfaces.bot.core.states import RecentSG
from src.interfaces.bot.dialogs.elements import on_cancel
from src.interfaces.bot.dialogs.getters.recent_errors import (
    recent_all_getter,
    recent_report_getter,
)
from src.interfaces.bot.dialogs.handlers.recent_errors import on_show_all_errors


def recent_viewing_report_window() -> Window:
    return Window(
        Format("{report_html}"),
        Button(
            Format("Show all {total_errors} errors"),
            id="show_all",
            on_click=on_show_all_errors,
            when="has_more_errors",
        ),
        Button(Const("⬅️ Main menu"), id="cancel", on_click=on_cancel),
        state=RecentSG.viewing_data,
        getter=recent_report_getter,
    )


def recent_viewing_all_window() -> Window:
    return Window(
        Format("{report_html_all}"),
        Button(Const("⬅️ Back"), id="cancel", on_click=on_cancel),
        state=RecentSG.viewing_all,
        getter=recent_all_getter,
    )
