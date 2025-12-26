from pydantic_settings import BaseSettings, SettingsConfigDict

from src.domain.entities.enums import ReportTemplate, ReportType


class ReportSettings(BaseSettings):
    analyze_template: str = ReportTemplate.ANALYSIS_DETAILED.value
    recent_template: str = ReportTemplate.RECENT_ERRORS.value
    stats_template: str = ReportTemplate.STATISTICS.value

    model_config = SettingsConfigDict(env_prefix="REPORT_", case_sensitive=False)

    def get_template(self, report_type: ReportType) -> str:
        match report_type:
            case ReportType.ANALYZE:
                return self.analyze_template
            case ReportType.RECENT:
                return self.recent_template
            case ReportType.STATS:
                return self.stats_template
            case ReportType.ANSWER:
                return ReportTemplate.ANSWER.value
            case _:
                raise ValueError("Unknown template")
