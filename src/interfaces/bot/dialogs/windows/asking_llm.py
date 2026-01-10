from aiogram_dialog import Window
from aiogram_dialog.widgets.kbd import Back, Cancel
from aiogram_dialog.widgets.text import Const, Format

from src.interfaces.bot.dialogs.getters.analyze_getters import ask_llm_report_getter
from src.interfaces.bot.entities import AnalyzeSG


def asking_llm_window() -> Window:
    return Window(
        Format("{answer_html}"),
        Const("You can ask more questions about this report, or write /menu to get back."),
        Back(Const("⬅️ Back")),
        Cancel(Const("Back to main menu")),
        state=AnalyzeSG.asking_questions,
        getter=ask_llm_report_getter,
    )
