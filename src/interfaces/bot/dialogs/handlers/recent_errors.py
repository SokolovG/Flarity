from logging import getLogger

import msgspec
from aiogram.types import CallbackQuery
from aiogram_dialog import DialogManager
from aiogram_dialog.widgets.kbd import Button
from dishka.integrations.aiogram import FromDishka
from dishka.integrations.aiogram_dialog import inject

from src.application.use_cases.get_recent_errors_use_case import RecentErrorsUseCase
from src.domain.value_objects.time_range import TimeRange
from src.interfaces.bot.core.states import MainSG, RecentSG
from src.interfaces.bot.utils.handlers_utils import (
    send_error_and_exit_dialog,
    send_no_errors_and_exit_dialog,
)
from src.interfaces.bot.utils.messages import error_msg, no_errors_msg, operation_failed_msg

logger = getLogger(__name__)


async def on_recent(callback: CallbackQuery, widget: Button, manager: DialogManager) -> None:
    await manager.start(RecentSG.period_selection)


async def on_show_all_errors(
    callback: CallbackQuery,
    widget: Button,
    manager: DialogManager,
) -> None:
    await manager.switch_to(RecentSG.viewing_all)


@inject
async def on_recent_period_click(
    callback: CallbackQuery,
    widget: Button,
    manager: DialogManager,
    use_case: FromDishka[RecentErrorsUseCase],
) -> None:
    try:
        period = int(widget.widget_id.split("_")[1])  # type: ignore
        time_range = TimeRange(period)
        report = await use_case.execute(time_range)

        if not report.has_errors:
            await send_no_errors_and_exit_dialog(callback, manager, time_range)
            return

        await callback.answer()
        manager.dialog_data.update({"report": msgspec.to_builtins(report)})
        await manager.switch_to(RecentSG.viewing_data)

    except Exception as e:
        logger.exception(operation_failed_msg(e))
        await send_error_and_exit_dialog(callback, manager)
