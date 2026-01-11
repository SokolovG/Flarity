from aiogram.types import CallbackQuery
from aiogram_dialog import DialogManager
from aiogram_dialog.widgets.kbd import Button
from dishka.integrations.aiogram import FromDishka
from dishka.integrations.aiogram_dialog import inject

from src.application.use_cases.get_statistics_use_case import StatisticsLogsUseCase
from src.domain.value_objects.time_range import TimeRange
from src.interfaces.bot.states import MainSG, StatsSG
from src.interfaces.bot.utils.messages import no_errors_msg


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
        period = int(widget.widget_id.split("_")[1])  # type: ignore
        time_range = TimeRange(period)

        report = await use_case.execute(time_range)
        if not report.has_errors:
            await callback.message.answer(no_errors_msg(time_range))  # type: ignore
            await manager.done()
            await manager.start(MainSG.menu)
            return

        manager.dialog_data.update({"report": report})
        await manager.switch_to(StatsSG.viewing_data)

    except Exception as e:
        manager.dialog_data.update({"report": e})
        await manager.done()
        await manager.switch_to(MainSG.menu)
