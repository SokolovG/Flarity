from typing import Self

from msgspec import Struct

from src.core.utils import format_hours
from src.domain.value_objects.time_range import TimeRange


class AnalysisResult(Struct):
    has_errors: bool
    report_html: str
    hours: TimeRange

    @staticmethod
    def no_errors(self, time_range: TimeRange) -> None:
        return None
