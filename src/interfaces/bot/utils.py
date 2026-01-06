from aiogram.fsm.context import FSMContext
from aiogram.types import CallbackQuery, InlineKeyboardMarkup

from src.interfaces.bot.entities import BotStates, MessageAction
from src.interfaces.bot.keyboards import get_main_menu

STATES_REQUIRING_NEW_MESSAGE = {
    BotStates.viewing_report,
    BotStates.start,
    BotStates.error,
}
STATES_REQUIRING_DELETE_MSG = {BotStates.period_selection}
STATES_REQUIRING_MAIN_MENU = {BotStates.period_selection, BotStates.waiting_for_question}


async def get_keyboard_from_state(state: FSMContext) -> InlineKeyboardMarkup | None:
    current_state = await state.get_state()
    if current_state in STATES_REQUIRING_MAIN_MENU:
        keyboard = get_main_menu()
        return keyboard
    return None


async def send_or_edit_message_from_state(
    callback: CallbackQuery,
    state: FSMContext,
    text: str,
    reply_markup: InlineKeyboardMarkup | None = None,
) -> None:
    if not callback.message:
        return

    current_state = await state.get_state()

    # TODO: баг, после отчета ллм меню, если вернутся после выбора периода меню удалится.
    # отчет - состояние viewing. нажали на back_menu -> main_menu. нажали на period_selection, потом назад = стейт у нас period_selection и менюшка удаляется
    if current_state in STATES_REQUIRING_DELETE_MSG:
        await callback.message.delete()  # type: ignore[union-attr]
        return

    if current_state in STATES_REQUIRING_NEW_MESSAGE:
        await callback.message.answer(text, reply_markup=reply_markup)
    else:
        await callback.message.edit_text(text, reply_markup=reply_markup)  # type: ignore[union-attr]
