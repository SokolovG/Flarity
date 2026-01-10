from aiogram_dialog import Window
from aiogram_dialog.widgets.text import Format

from src.interfaces.bot.dialogs.getters.help_getters import help_getter
from src.interfaces.bot.dialogs.getters.recent_getters import recent_all_getter
from src.interfaces.bot.entities import HelpSG


def help_window() -> Window:
    return Window(
        Format("{help_info}"), state=HelpSG.viewing_data, getter=help_getter, parse_mode="HTML"
    )
