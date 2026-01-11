from aiogram_dialog import Dialog

from src.interfaces.bot.core.states import AnalyzeSG, RecentSG, StatsSG
from src.interfaces.bot.dialogs.handlers.llm_analyze import on_analyze_period_click
from src.interfaces.bot.dialogs.handlers.recent_errors import on_recent_period_click
from src.interfaces.bot.dialogs.handlers.stats import on_stats_period_click
from src.interfaces.bot.dialogs.windows.llm_analyze import (
    analyze_viewing_report_window,
    asking_llm_window,
)
from src.interfaces.bot.dialogs.windows.period_selection import period_selection_window
from src.interfaces.bot.dialogs.windows.recent_errors import (
    recent_viewing_all_window,
    recent_viewing_report_window,
)
from src.interfaces.bot.dialogs.windows.static_windows import (
    bug_window,
    help_window,
    menu_window,
    settings_window,
)
from src.interfaces.bot.dialogs.windows.stats import stats_viewing_report_window

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
