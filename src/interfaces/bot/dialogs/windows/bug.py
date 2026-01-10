from aiogram_dialog import Window

from src.interfaces.bot.entities import BugSG


def bug_window() -> Window:
    return Window(state=BugSG.reporting)
