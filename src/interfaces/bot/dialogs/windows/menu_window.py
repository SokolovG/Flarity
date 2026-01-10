from typing import Any

from aiogram.types import CallbackQuery, Message
from aiogram_dialog import DialogManager, Window
from aiogram_dialog.widgets.kbd import Button, Column
from aiogram_dialog.widgets.text import Const

from src.interfaces.bot.entities import AnalyzeSG, MainSG, RecentSG, SettingsSG, StatsSG
from src.interfaces.bot.messages import choose_an_action_msg


async def on_analyze(callback: CallbackQuery, widget: Any, manager: DialogManager) -> None:
    await manager.start(AnalyzeSG.period_selection)


async def on_stats(callback: CallbackQuery, widget: Any, manager: DialogManager) -> None:
    await manager.start(StatsSG.period_selection)


async def on_recent(callback: CallbackQuery, widget: Any, manager: DialogManager) -> None:
    await manager.start(RecentSG.period_selection)


async def on_settings(callback: CallbackQuery, widget: Any, manager: DialogManager) -> None:
    await manager.start(SettingsSG.viewing_data)


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
