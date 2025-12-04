from src.entities.report import ReportData


class ReportFormatter:
    @staticmethod
    def to_html(data: ReportData) -> str:
        return f"""
            <b>{data.title}</b>

            Статистика за {data.time_range_hours}ч:
            - Всего ошибок: {data.total_errors}
            - Уникальных типов: {data.unique_types}

            AI Анализ:
            {data.ai_analysis}
            """
