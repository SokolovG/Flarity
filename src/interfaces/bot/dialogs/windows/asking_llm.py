from aiogram_dialog import Window
from aiogram_dialog.widgets.input import MessageInput
from aiogram_dialog.widgets.kbd import Back, Button
from aiogram_dialog.widgets.text import Const, Format

from src.interfaces.bot.dialogs.elements import on_cancel
from src.interfaces.bot.dialogs.getters.analyze_getters import ask_llm_report_getter
from src.interfaces.bot.dialogs.handlers.llm_question import on_llm_question
from src.interfaces.bot.states import AnalyzeSG


def asking_llm_window() -> Window:
    return Window(
        Format("{answer_html}"),
        Const("You can ask more questions about this report, or write /menu to get back."),
        Back(Const("⬅️ Back")),
        Button(Const("⬅️ Back"), id="cancel", on_click=on_cancel),
        MessageInput(on_llm_question),
        state=AnalyzeSG.asking_questions,
        getter=ask_llm_report_getter,
    )
