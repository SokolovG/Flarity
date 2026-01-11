from aiogram_dialog import Window
from aiogram_dialog.widgets.input import MessageInput
from aiogram_dialog.widgets.kbd import Cancel
from aiogram_dialog.widgets.text import Const, Format

from src.interfaces.bot.dialogs.getters.bug_getters import bug_been_sent_getter, bug_getter
from src.interfaces.bot.dialogs.handlers.bug_report import on_bug_report
from src.interfaces.bot.states import BugSG


def bug_window() -> Window:
    return Window(
        Format("{report_bug}"),
        Cancel(Const("⬅️ Back")),
        state=BugSG.viewing_instructions,
        getter=bug_getter,
    )


def bug_send_window() -> Window:
    return Window(
        Format("{msg_been_sent}"),
        MessageInput(on_bug_report),
        state=BugSG.reporting,
        getter=bug_been_sent_getter,
    )
