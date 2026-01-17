from logging import getLogger

import msgspec
from aiogram.types import CallbackQuery
from aiogram_dialog import DialogManager
from aiogram_dialog.widgets.kbd import Button
from dishka.integrations.aiogram import FromDishka
from dishka.integrations.aiogram_dialog import inject

from src.application.use_cases.get_statistics_use_case import StatisticsLogsUseCase
from src.domain.value_objects.time_range import TimeRange
from src.interfaces.bot.core.states import StatsSG
from src.interfaces.bot.utils.error_handler import handle_bot_error
from src.interfaces.bot.utils.handlers_utils import (
    send_no_errors_and_exit_dialog,
)

logger = getLogger(__name__)


async def on_stats(callback: CallbackQuery, widget: Button, manager: DialogManager) -> None:
    await manager.start(StatsSG.period_selection)


@inject
async def on_stats_period_click(
    callback: CallbackQuery,
    widget: Button,
    manager: DialogManager,
    use_case: FromDishka[StatisticsLogsUseCase],
) -> None:
    try:
        period = int(widget.widget_id.split("_")[1])  # type:ignore[union-attr]
        time_range = TimeRange(period)
        report = await use_case.execute(time_range)

        if not report.has_errors:
            await send_no_errors_and_exit_dialog(callback, manager, time_range)
            return

        await callback.answer()
        manager.dialog_data.update({"report": msgspec.to_builtins(report)})
        await manager.switch_to(StatsSG.viewing_data)

    except Exception as e:
        await handle_bot_error(e, callback, manager, context="stats_period_selection")
