from aiogram_dialog import Window
from aiogram_dialog.widgets.input import MessageInput
from aiogram_dialog.widgets.kbd import Back, Button
from aiogram_dialog.widgets.text import Const, Format

from src.interfaces.bot.core.states import AnalyzeSG
from src.interfaces.bot.dialogs.elements import on_cancel
from src.interfaces.bot.dialogs.getters.llm_analyze import (
    analyze_report_getter,
    ask_llm_report_getter,
)
from src.interfaces.bot.dialogs.handlers.llm_analyze import on_llm_question


def analyze_viewing_report_window() -> Window:
    return Window(
        Format("{report_html}"),
        Const("You can ask questions about this report."),
        MessageInput(on_llm_question),
        Back(Const("⬅️ Back")),
        state=AnalyzeSG.viewing_data,
        getter=analyze_report_getter,
    )


def asking_llm_window() -> Window:
    # TODO: при выходе на менб теряется отчет
    return Window(
        Format("{answer_html}"),
        Const("You can ask more questions about this report, or write /menu to get back."),
        Button(Const("⬅️ Back"), id="cancel", on_click=on_cancel),
        MessageInput(on_llm_question),
        state=AnalyzeSG.asking_questions,
        getter=ask_llm_report_getter,
    )
