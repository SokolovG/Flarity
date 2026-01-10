from aiogram_dialog import Window

from src.interfaces.bot.entities import AnalyzeSG


def analyze_viewing_report_window() -> Window:
    return Window(state=AnalyzeSG.viewing_data)
