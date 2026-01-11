from logging import getLogger

from aiogram.types import CallbackQuery
from aiogram_dialog import DialogManager
from aiogram_dialog.widgets.kbd import Button
from dishka.integrations.aiogram import FromDishka
from dishka.integrations.aiogram_dialog import inject

from src.application.use_cases.analyze_logs_use_case import AnalyzeLogsUseCase
from src.domain.value_objects.time_range import TimeRange
from src.interfaces.bot.states import AnalyzeSG, MainSG
from src.interfaces.bot.utils.messages import loading_msg, no_errors_msg

logger = getLogger(__name__)


async def on_analyze(callback: CallbackQuery, widget: Button, manager: DialogManager) -> None:
    await manager.start(AnalyzeSG.period_selection)


@inject
async def on_analyze_period_click(
    callback: CallbackQuery,
    widget: Button,
    manager: DialogManager,
    use_case: FromDishka[AnalyzeLogsUseCase],
) -> None:
    try:
        await callback.answer()
        period = int(widget.widget_id.split("_")[1])  # type: ignore
        time_range = TimeRange(period)
        load_msg = await callback.message.answer(loading_msg(time_range))  # type: ignore[union-attr]
        user_id = str(callback.from_user.id)

        report = await use_case.execute(time_range, user_id)
        if not report.has_errors:
            await load_msg.edit_text(no_errors_msg(time_range))
            await manager.done()
            await manager.start(MainSG.menu)
            return

        await load_msg.delete()
        manager.dialog_data.update({"report": report})
        await manager.switch_to(AnalyzeSG.viewing_data)

    except Exception as e:
        logger.exception(f"Operation failed: {e}")
        await callback.message.answer("❌ Something went wrong. Try again.")  # type: ignore[union-attr]
        await manager.done()
        await manager.start(MainSG.menu)
