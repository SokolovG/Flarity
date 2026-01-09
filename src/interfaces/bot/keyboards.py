from aiogram.types import InlineKeyboardButton, InlineKeyboardMarkup

from src.domain import TimeRange
from src.interfaces.bot.constants import PERIODS
from src.interfaces.bot.entities import BotAction, BotCallback


def get_main_menu() -> InlineKeyboardMarkup:
    keyboard = InlineKeyboardMarkup(
        inline_keyboard=[
            [InlineKeyboardButton(text="LLM analysis", callback_data=BotCallback.ANALYZE.value)],
            [InlineKeyboardButton(text="Statistics", callback_data=BotCallback.STATS.value)],
            [InlineKeyboardButton(text="Recent errors", callback_data=BotCallback.RECENT.value)],
            [InlineKeyboardButton(text="Settings", callback_data=BotCallback.SETTINGS.value)],
        ]
    )
    return keyboard


def get_period_options(action: BotAction, periods: list[int] = PERIODS) -> InlineKeyboardMarkup:
    buttons: list[list[InlineKeyboardButton]] = []
    for period in periods:
        btn = [
            InlineKeyboardButton(
                text=f"{(TimeRange(period).hour_and_unit)}",
                callback_data=f"{action.value}_{period}",
            )
        ]
        buttons.append(btn)
    buttons.append(
        [InlineKeyboardButton(text="Back to menu", callback_data=BotCallback.BACK_TO_MENU.value)]
    )
    keyboard = InlineKeyboardMarkup(inline_keyboard=buttons)

    return keyboard


def get_back_to_menu_button() -> InlineKeyboardMarkup:
    return InlineKeyboardMarkup(
        inline_keyboard=[
            [
                InlineKeyboardButton(
                    text="Back to menu", callback_data=BotCallback.BACK_TO_MENU.value
                )
            ]
        ]
    )


def get_more_errors_menu(errors_count: int) -> InlineKeyboardMarkup:
    return InlineKeyboardMarkup(
        inline_keyboard=[
            [
                InlineKeyboardButton(
                    text="Back to menu", callback_data=BotCallback.BACK_TO_MENU.value
                )
            ],
            [
                InlineKeyboardButton(
                    text=f"Show all {errors_count} errors",
                    callback_data=BotCallback.YES_RECENT.value,
                )
            ],
        ]
    )
