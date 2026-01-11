from aiogram_dialog import Window
from aiogram_dialog.widgets.input import MessageInput
from aiogram_dialog.widgets.kbd import Button
from aiogram_dialog.widgets.text import Const, Format

from src.interfaces.bot.dialogs.elements import on_cancel
from src.interfaces.bot.dialogs.getters.bug_getters import bug_getter
from src.interfaces.bot.dialogs.handlers.bug_report import on_bug_report
from src.interfaces.bot.states import BugSG


def bug_window() -> Window:
    # TODO: сохранять ллм сессию. щас ошибка что ее не
    # TODO: после 1 отправленного бага дальше при вызове команды баг вызывается главное менб
    return Window(
        Format("{report_bug}"),
        MessageInput(on_bug_report),
        Button(Const("⬅️ Back"), id="cancel", on_click=on_cancel),
        state=BugSG.reporting,
        getter=bug_getter,
    )
