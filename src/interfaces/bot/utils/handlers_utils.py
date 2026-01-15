from aiogram.types import CallbackQuery
from aiogram_dialog import DialogManager

from src.domain.value_objects.time_range import TimeRange
from src.interfaces.bot.core.states import MainSG
from src.interfaces.bot.utils.messages import error_msg, no_errors_msg


async def send_no_errors_and_exit_dialog(
    callback: CallbackQuery,
    manager: DialogManager,
    time_range: TimeRange,
) -> None:
    await callback.answer()
    await callback.message.answer(no_errors_msg(time_range))  # type: ignore
    await manager.done()
    await manager.start(MainSG.menu)


async def send_error_and_exit_dialog(
    callback: CallbackQuery,
    manager: DialogManager,
) -> None:
    await callback.answer()
    await callback.message.answer(error_msg())  # type: ignore
    await manager.done()
    await manager.start(MainSG.menu)
