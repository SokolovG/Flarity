from aiogram.types import CallbackQuery
from aiogram_dialog import DialogManager
from aiogram_dialog.widgets.kbd import Button
from dishka.integrations.aiogram import FromDishka
from dishka.integrations.aiogram_dialog import inject

from src.application.use_cases.analyze_logs_use_case import AnalyzeLogsUseCase
from src.domain.value_objects.time_range import TimeRange
from src.interfaces.bot.entities import AnalyzeSG


async def on_analyze(callback: CallbackQuery, widget: Button, manager: DialogManager) -> None:
    await manager.start(AnalyzeSG.period_selection)


@inject
async def on_analyze_period_click(
    callback: CallbackQuery,
    widget: Button,
    manager: DialogManager,
    use_case: FromDishka[AnalyzeLogsUseCase],
) -> None:
    period = int(widget.widget_id.split("_")[1])  # type: ignore
    user_id = str(callback.from_user.id)

    report = await use_case.execute(TimeRange(period), user_id)
    manager.dialog_data.update({"report": report})
    await manager.switch_to(AnalyzeSG.viewing_data)
