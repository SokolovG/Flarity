from enum import Enum

from aiogram.fsm.state import State, StatesGroup


class BotAction(Enum):
    ANALYZE = "analyze"
    RECENT = "recent"
    STATS = "stats"


class BotCallback(str, Enum):
    ANALYZE = "analyze"
    STATS = "stats"
    RECENT = "recent"
    SETTINGS = "settings"
    BACK_TO_MENU = "back_to_menu"


class BotStates(StatesGroup):
    main_menu = State()
    period_selection = State()
    viewing_report = State()
