from aiogram_dialog import Window
from aiogram_dialog.widgets.kbd import Back, Cancel
from aiogram_dialog.widgets.text import Const, Format

from src.interfaces.bot.dialogs.getters.stats_getters import stats_report_getter
from src.interfaces.bot.entities import StatsSG


def stats_viewing_report_window() -> Window:
    return Window(
        Format("{report_html}"),
        Back(Const("⬅️ Back")),
        Cancel(Const("⬅️ To main menu")),
        state=StatsSG.viewing_data,
        getter=stats_report_getter,
    )
