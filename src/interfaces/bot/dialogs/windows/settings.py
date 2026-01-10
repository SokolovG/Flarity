from aiogram_dialog import Window

from src.interfaces.bot.entities import SettingsSG


def settings_window() -> Window:
    return Window(state=SettingsSG.viewing_data)
