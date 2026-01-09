from enum import Enum

from aiogram.fsm.state import State, StatesGroup


class BotAction(Enum):
    ANALYZE = "analyze"
    RECENT = "recent"
    STATS = "stats"
    SETTINGS = "settings"
    HELP = "help"
    ASK = "ask"
    MENU = "menu"
    BUG = "bug"


class BotCallback(str, Enum):
    ANALYZE = "analyze"
    STATS = "stats"
    RECENT = "recent"
    SETTINGS = "settings"
    BACK_TO_MENU = "back_to_menu"
    YES = "yes"
    NO = "no"
    YES_RECENT = "yes_recent"


class MessageAction(Enum):
    EDIT = "edit"
    NEW = "new"
    REPLACE = "replace"


class BotStates(StatesGroup):
    main_menu = State()
    period_selection = State()
    viewing_data = State()
    waiting_for_question = State()
    start = State()
    reporting_bug = State()
