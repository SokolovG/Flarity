from aiogram.types import InlineKeyboardButton, InlineKeyboardMarkup


def get_main_menu() -> InlineKeyboardMarkup:
    keyboard = InlineKeyboardMarkup(
        inline_keyboard=[
            [InlineKeyboardButton(text="LLM analysis", callback_data="llm_analysis")],
            [InlineKeyboardButton(text="Statistics", callback_data="statistics")],
            [InlineKeyboardButton(text="Recent errors", callback_data="recent")],
            [InlineKeyboardButton(text="Settings", callback_data="settings")],
        ]
    )
    return keyboard


def get_analysis_options() -> InlineKeyboardMarkup:
    keyboard = InlineKeyboardMarkup(
        inline_keyboard=[
            [InlineKeyboardButton(text="1 hour", callback_data="analyze_1")],
            [InlineKeyboardButton(text="6 hours", callback_data="analyze_6")],
            [InlineKeyboardButton(text="12 hours", callback_data="analyze_12")],
            [InlineKeyboardButton(text="24 hours", callback_data="analyze_24")],
            [InlineKeyboardButton(text="Back to menu", callback_data="back_to_menu")],
        ]
    )
    return keyboard


def get_recent_options() -> InlineKeyboardMarkup:
    keyboard = InlineKeyboardMarkup(
        inline_keyboard=[
            [InlineKeyboardButton(text="1 hour", callback_data="recent_1")],
            [InlineKeyboardButton(text="6 hours", callback_data="recent_6")],
            [InlineKeyboardButton(text="12 hours", callback_data="recent_12")],
            [InlineKeyboardButton(text="24 hours", callback_data="recent_24")],
            [InlineKeyboardButton(text="Back to menu", callback_data="back_to_menu")],
        ]
    )
    return keyboard


def get_back_to_menu_button() -> InlineKeyboardMarkup:
    return InlineKeyboardMarkup(
        inline_keyboard=[[InlineKeyboardButton(text="Back to menu", callback_data="back_to_menu")]]
    )


def get_settings() -> InlineKeyboardMarkup:
    return InlineKeyboardMarkup(
        inline_keyboard=[
            [
                InlineKeyboardButton(
                    text="Enable schedule notification", callback_data="enable_schedule"
                )
            ],
        ]
    )
