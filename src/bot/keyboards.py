from aiogram.types import InlineKeyboardButton, InlineKeyboardMarkup


def get_start_keyboard() -> InlineKeyboardMarkup:
    keyboard = InlineKeyboardMarkup(
        inline_keyboard=[
            InlineKeyboardButton(text="", callback_data=""),
            InlineKeyboardButton(text="", callback_data=""),
        ]
    )
    return keyboard
