from aiogram.fsm.state import State, StatesGroup


class MainSG(StatesGroup):
    menu = State()


class AnalyzeSG(StatesGroup):
    period_selection = State()
    viewing_data = State()
    asking_questions = State()


class RecentSG(StatesGroup):
    period_selection = State()
    viewing_data = State()
    viewing_all = State()


class StatsSG(StatesGroup):
    period_selection = State()
    viewing_data = State()


class SettingsSG(StatesGroup):
    viewing_data = State()


class BugSG(StatesGroup):
    reporting = State()


class HelpSG(StatesGroup):
    viewing_data = State()


class ScheduledSG(StatesGroup):
    asking_questions = State()
