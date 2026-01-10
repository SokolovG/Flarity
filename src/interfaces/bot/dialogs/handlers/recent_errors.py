from aiogram.types import CallbackQuery
from aiogram_dialog import DialogManager
from aiogram_dialog.widgets.kbd import Button
from dishka.integrations.aiogram import FromDishka
from dishka.integrations.aiogram_dialog import inject

from src.application.dto.analysis_report import AnalysisReport
from src.application.use_cases.get_recent_errors_use_case import RecentErrorsUseCase
from src.domain.entities.enums import ReportType
from src.domain.value_objects.time_range import TimeRange
from src.interfaces.bot.entities import RecentSG
from src.interfaces.bot.formatters.html_formatter import ReportFormatter
from src.interfaces.bot.messages import no_errors_msg


async def on_recent(callback: CallbackQuery, widget: Button, manager: DialogManager) -> None:
    await manager.start(RecentSG.period_selection)


@inject
async def on_show_all_errors(
    callback: CallbackQuery,
    widget: Button,
    manager: DialogManager,
    formatter: FromDishka[ReportFormatter],
) -> None:
    report: AnalysisReport = manager.dialog_data.get("report")  # type:ignore

    html = formatter.to_html(report, ReportType.RECENT, show_all_errors=True)
    await callback.message.answer(html)
    await callback.message.edit_reply_markup(reply_markup=None)


@inject
async def on_recent_period_click(
    callback: CallbackQuery,
    widget: Button,
    manager: DialogManager,
    use_case: FromDishka[RecentErrorsUseCase],
) -> None:
    period = int(widget.widget_id.split("_")[1])
    time_range = TimeRange(period)

    report = await use_case.execute(time_range)
    if not report.has_errors:
        await callback.message.answer(no_errors_msg(time_range))
        return

    manager.dialog_data.update({"report": report})
    await manager.switch_to(RecentSG.viewing_data)
