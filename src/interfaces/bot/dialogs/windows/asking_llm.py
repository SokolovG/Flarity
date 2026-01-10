from aiogram_dialog import Window

from src.interfaces.bot.entities import AnalyzeSG


def asking_llm_window() -> Window:
    return Window(state=AnalyzeSG.asking_questions)
