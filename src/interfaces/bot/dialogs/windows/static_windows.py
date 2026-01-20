from aiogram_dialog import Window
from aiogram_dialog.widgets.input import MessageInput
from aiogram_dialog.widgets.kbd import Button, Column
from aiogram_dialog.widgets.text import Const, Format

from src.interfaces.bot.core.elements import on_cancel
from src.interfaces.bot.core.states import BugSG, HelpSG, MainSG, SettingsSG
from src.interfaces.bot.dialogs.getters.static import bug_getter, help_getter, settings_getter
from src.interfaces.bot.dialogs.handlers.bug_report import on_bug_report
from src.interfaces.bot.dialogs.handlers.llm_analyze import on_analyze
from src.interfaces.bot.dialogs.handlers.recent_errors import on_recent
from src.interfaces.bot.dialogs.handlers.static import on_settings
from src.interfaces.bot.dialogs.handlers.stats import on_stats
from src.interfaces.bot.utils.dialogs_utils import handle_unknown_text_in_dialog
from src.interfaces.bot.utils.messages import greetings_msg


def menu_window() -> Window:
    return Window(
        Const(greetings_msg()),
        MessageInput(handle_unknown_text_in_dialog),
        Column(
            Button(Const("Analyze"), id="analyze", on_click=on_analyze),
            Button(Const("Stats"), id="stats", on_click=on_stats),
            Button(Const("Recent"), id="recent", on_click=on_recent),
            Button(Const("Settings"), id="settings", on_click=on_settings),
        ),
        state=MainSG.menu,
    )


def help_window() -> Window:
    return Window(
        Format("{help_info}"),
        MessageInput(handle_unknown_text_in_dialog),
        Button(Const("⬅️ Back"), id="cancel", on_click=on_cancel),
        state=HelpSG.viewing_data,
        getter=help_getter,
        parse_mode="HTML",
    )


def settings_window() -> Window:
    return Window(
        Format("{settings_info}"),
        MessageInput(handle_unknown_text_in_dialog),
        Button(Const("⬅️ Back"), id="cancel", on_click=on_cancel),
        state=SettingsSG.viewing_data,
        getter=settings_getter,
    )


def bug_window() -> Window:
    return Window(
        Format("{report_bug}"),
        MessageInput(on_bug_report),  # ty: ignore[invalid-argument-type]
        Button(Const("⬅️ Back"), id="cancel", on_click=on_cancel),
        state=BugSG.reporting,
        getter=bug_getter,
    )
