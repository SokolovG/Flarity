from jinja2 import Environment, FileSystemLoader

from src.domain.entities.enums import ReportTemplate
from src.domain.entities.report import ReportData


class ReportFormatter:
    def __init__(self) -> None:
        self.env = Environment(loader=FileSystemLoader("templates"), autoescape=True)

    def to_html(
        self, data: ReportData, template_name: ReportTemplate = ReportTemplate.ANALYSIS_DETAILED
    ) -> str:
        template = self.env.get_template(template_name.value)
        return template.render(
            title=data.title,
            time_range_hours=data.time_range_hours,
            total_errors=data.total_errors,
            unique_types=data.unique_types,
            logs=data.logs,
            groups=data.groups,
            ai_analysis=data.ai_analysis,
            provider=data.provider,
            tokens_in=data.tokens_in,
            tokens_out=data.tokens_out,
        )
