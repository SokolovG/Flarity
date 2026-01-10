from aiogram_dialog import Window
from aiogram_dialog.widgets.input import MessageInput
from aiogram_dialog.widgets.kbd import Back
from aiogram_dialog.widgets.text import Const, Format

from src.interfaces.bot.dialogs.getters.analyze_getters import analyze_report_getter
from src.interfaces.bot.dialogs.handlers.llm_question import on_llm_question
from src.interfaces.bot.states import AnalyzeSG


def analyze_viewing_report_window() -> Window:
    return Window(
        Format("{report_html}"),
        Const("You can ask questions about this report."),
        MessageInput(on_llm_question),
        Back(Const("⬅️ Back")),
        state=AnalyzeSG.viewing_data,
        getter=analyze_report_getter,
    )
