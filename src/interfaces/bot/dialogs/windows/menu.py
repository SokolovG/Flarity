from aiogram_dialog import Window
from aiogram_dialog.widgets.kbd import Button, Column
from aiogram_dialog.widgets.text import Const

from src.interfaces.bot.callbacks import on_settings
from src.interfaces.bot.dialogs.handlers.analyze_handlers import on_analyze
from src.interfaces.bot.dialogs.handlers.recent_handlers import on_recent
from src.interfaces.bot.dialogs.handlers.stats_handlers import on_stats
from src.interfaces.bot.entities import MainSG
from src.interfaces.bot.messages import choose_an_action_msg


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
