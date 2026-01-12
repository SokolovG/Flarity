from aiogram_dialog import Window
from aiogram_dialog.widgets.input import MessageInput
from aiogram_dialog.widgets.kbd import Back, Button
from aiogram_dialog.widgets.text import Const, Format

from src.interfaces.bot.core.elements import on_cancel
from src.interfaces.bot.core.states import AnalyzeSG
from src.interfaces.bot.dialogs.getters.llm_analyze import (
    analyze_report_getter,
    ask_llm_report_getter,
)
from src.interfaces.bot.dialogs.handlers.llm_analyze import on_llm_question
from src.interfaces.bot.utils.messages import ask_llm_more_questions, ask_llm_msg


def analyze_viewing_report_window() -> Window:
    return Window(
        Format("{report_html}"),
        Const(ask_llm_msg()),
        MessageInput(on_llm_question),
        Back(Const("⬅️ Back")),
        state=AnalyzeSG.viewing_data,
        getter=analyze_report_getter,
    )


def asking_llm_window() -> Window:
    # TODO: при выходе на менб теряется отчет
    return Window(
        Format("{answer_html}"),
        Const(ask_llm_more_questions()),
        Button(Const("⬅️ Back"), id="cancel", on_click=on_cancel),
        MessageInput(on_llm_question),
        state=AnalyzeSG.asking_questions,
        getter=ask_llm_report_getter,
    )
