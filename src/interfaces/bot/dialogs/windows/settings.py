from aiogram_dialog import Window
from aiogram_dialog.widgets.kbd import Cancel
from aiogram_dialog.widgets.text import Const, Format

from src.interfaces.bot.dialogs.getters.settings_getter import settings_getter
from src.interfaces.bot.entities import SettingsSG


def settings_window() -> Window:
    return Window(
        Format("{settings_info}"),
        Cancel(Const("⬅️ Back")),
        state=SettingsSG.viewing_data,
        getter=settings_getter,
    )
