from aiogram_dialog import Window

from src.interfaces.bot.entities import RecentSG


def recent_viewing_report_window() -> Window:
    return Window(state=RecentSG.viewing_data)
