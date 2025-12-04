from src.clients import TelegramClient
from src.core.settings.notification_settings import NotificationSettings
from src.entities.report import ReportData
from src.responses import LLMAnalysisResult, LogsByErrorType
from src.services.base_services import BaseNotificationService
from src.services.report_formatter_service import ReportFormatter


class NotificationService(BaseNotificationService):
    def __init__(self, telegram_client: TelegramClient, settings: NotificationSettings):
        self.telegram_client = telegram_client
        self.settings = settings

    async def send_analysis_report(
        self, analysis: LLMAnalysisResult, grouped_logs: LogsByErrorType, time_range_hours: int = 24
    ) -> bool:
        report = self._format_report(analysis, grouped_logs, time_range_hours)
        return await self.telegram_client.send_message(report)

    def _format_report(
        self, analysis: LLMAnalysisResult, grouped_logs: LogsByErrorType, time_range_hours: int
    ) -> str:
        total_errors = sum(len(group.logs) for group in grouped_logs.logs_groups)
        report_data = ReportData(
            title="<b>Отчет по ошибкам за последний час</b>\n",
            time_range_hours=time_range_hours,
            total_errors=total_errors,
            unique_types=len(grouped_logs.logs_groups),
            ai_analysis=analysis.analysis_text,
            # top_errors=[],
            provider=analysis.provider.value,
            tokens_in=analysis.input_tokens_used,
            tokens_out=analysis.output_tokens_used,
        )
        msg = ReportFormatter.to_html(report_data)
        return msg
