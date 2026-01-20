from aiogram.types import CallbackQuery
from aiogram_dialog import DialogManager

from src.domain.value_objects.time_range import TimeRange
from src.interfaces.bot.core.states import MainSG
from src.interfaces.bot.utils.messages import no_errors_msg


async def send_no_errors_and_exit_dialog(
    callback: CallbackQuery,
    manager: DialogManager,
    time_range: TimeRange,
) -> None:
    await callback.answer()
    if callback.message:
        await callback.message.answer(no_errors_msg(time_range))
    await manager.done()
    await manager.start(MainSG.menu)
