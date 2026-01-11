from aiogram_dialog import Window
from aiogram_dialog.widgets.kbd import Back, Button
from aiogram_dialog.widgets.text import Const, Format

from src.interfaces.bot.dialogs.elements import on_cancel
from src.interfaces.bot.dialogs.getters.stats_getters import stats_report_getter
from src.interfaces.bot.states import StatsSG


def stats_viewing_report_window() -> Window:
    return Window(
        Format("{report_html}"),
        Button(Const("⬅️ Main menu"), id="cancel", on_click=on_cancel),
        state=StatsSG.viewing_data,
        getter=stats_report_getter,
    )
