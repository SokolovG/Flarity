from aiogram_dialog import Window

from src.interfaces.bot.entities import StatsSG


def stats_viewing_report_window() -> Window:
    return Window(state=StatsSG.viewing_data)
