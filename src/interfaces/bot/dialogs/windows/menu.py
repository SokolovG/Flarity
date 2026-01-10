from aiogram_dialog import Window
from aiogram_dialog.widgets.kbd import Button, Column
from aiogram_dialog.widgets.text import Const

from src.interfaces.bot.dialogs.handlers.analyze import on_analyze
from src.interfaces.bot.dialogs.handlers.recent_errors import on_recent
from src.interfaces.bot.dialogs.handlers.settings import on_settings
from src.interfaces.bot.dialogs.handlers.stats import on_stats
from src.interfaces.bot.states import MainSG
from src.interfaces.bot.utils.messages import choose_an_action_msg


def menu_window() -> Window:
    return Window(
        Const(choose_an_action_msg()),
        Column(
            Button(Const("Analyze"), id="analyze", on_click=on_analyze),
            Button(Const("Stats"), id="stats", on_click=on_stats),
            Button(Const("Recent"), id="recent", on_click=on_recent),
            Button(Const("Settings"), id="settings", on_click=on_settings),
        ),
        state=MainSG.menu,
    )
