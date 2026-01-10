from aiogram_dialog import Window

from src.interfaces.bot.states import BugSG


def bug_window() -> Window:
    return Window(state=BugSG.reporting)
