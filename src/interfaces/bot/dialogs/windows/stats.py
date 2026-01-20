from aiogram_dialog import Window
from aiogram_dialog.widgets.input import MessageInput
from aiogram_dialog.widgets.kbd import Button
from aiogram_dialog.widgets.text import Const, Format

from src.interfaces.bot.core.elements import on_cancel
from src.interfaces.bot.core.states import StatsSG
from src.interfaces.bot.dialogs.getters.stats import stats_report_getter
from src.interfaces.bot.utils.dialogs_utils import handle_unknown_text_in_dialog


def stats_viewing_report_window() -> Window:
    return Window(
        Format("{report_html}"),
        MessageInput(handle_unknown_text_in_dialog),
        Button(Const("⬅️ Main menu"), id="cancel", on_click=on_cancel),
        state=StatsSG.viewing_data,
        getter=stats_report_getter,
    )
