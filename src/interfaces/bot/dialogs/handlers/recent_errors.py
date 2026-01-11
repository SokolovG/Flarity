from logging import getLogger

from aiogram.types import CallbackQuery
from aiogram_dialog import DialogManager
from aiogram_dialog.widgets.kbd import Button
from dishka.integrations.aiogram import FromDishka
from dishka.integrations.aiogram_dialog import inject

from src.application.use_cases.get_recent_errors_use_case import RecentErrorsUseCase
from src.domain.value_objects.time_range import TimeRange
from src.interfaces.bot.states import MainSG, RecentSG
from src.interfaces.bot.utils.messages import no_errors_msg

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
            await callback.message.answer(no_errors_msg(time_range))  # type: ignore
            await manager.done()
            await manager.start(MainSG.menu)
            return

        manager.dialog_data.update({"report": report})
        await manager.switch_to(RecentSG.viewing_data)

    except Exception as e:
        logger.exception(f"Operation failed: {e}")
        await callback.message.answer("❌ Something went wrong. Try again.")  # type: ignore[union-attr]
        await manager.done()
        await manager.start(MainSG.menu)
