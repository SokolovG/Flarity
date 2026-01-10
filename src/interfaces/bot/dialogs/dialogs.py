from aiogram_dialog import Dialog

from src.interfaces.bot.dialogs.handlers.analyze import on_analyze_period_click
from src.interfaces.bot.dialogs.handlers.recent_errors import on_recent_period_click
from src.interfaces.bot.dialogs.handlers.stats import on_stats_period_click
from src.interfaces.bot.dialogs.windows.analyze_viewing_report import analyze_viewing_report_window
from src.interfaces.bot.dialogs.windows.asking_llm import asking_llm_window
from src.interfaces.bot.dialogs.windows.bug import bug_window
from src.interfaces.bot.dialogs.windows.help import help_window
from src.interfaces.bot.dialogs.windows.menu import menu_window
from src.interfaces.bot.dialogs.windows.period_selection import period_selection_window
from src.interfaces.bot.dialogs.windows.recent_viewing_all import recent_viewing_all_window
from src.interfaces.bot.dialogs.windows.recent_viewing_report import recent_viewing_report_window
from src.interfaces.bot.dialogs.windows.settings import settings_window
from src.interfaces.bot.dialogs.windows.stats_viewing_report import stats_viewing_report_window
from src.interfaces.bot.states import AnalyzeSG, RecentSG, StatsSG

main_menu_dialog = Dialog(menu_window())
analyze_dialog = Dialog(
    period_selection_window(AnalyzeSG, on_analyze_period_click),
    analyze_viewing_report_window(),
    asking_llm_window(),
)
stats_dialog = Dialog(
    period_selection_window(StatsSG, on_stats_period_click), stats_viewing_report_window()
)
recent_dialog = Dialog(
    period_selection_window(RecentSG, on_recent_period_click),
    recent_viewing_report_window(),
    recent_viewing_all_window(),
)
settings_dialog = Dialog(settings_window())
bug_dialog = Dialog(bug_window())
help_dialog = Dialog(help_window())
