from datetime import datetime
from typing import Tuple, List

from dateutil.relativedelta import relativedelta
from dateutil.tz import tzutc


class MonthlyReportingWindow:
    @classmethod
    def prior_to(cls, date_anchor: datetime, number_of_months: int):
        overflow_month_start = datetime(date_anchor.year, date_anchor.month, 1, tzinfo=tzutc())
        metric_month_start = overflow_month_start - relativedelta(months=1)
        metric_months = [
            metric_month_start - relativedelta(months=number) for number in range(number_of_months)
        ]
        return cls(metric_month_start, overflow_month_start, metric_months)

    def __init__(
        self,
        metric_month_start: datetime,
        overflow_month_start: datetime,
        metric_months: List[datetime],
    ):
        self._metric_month_start = metric_month_start
        self._overflow_month_start = overflow_month_start
        self._metric_months = metric_months

    @property
    def metric_month(self) -> int:
        return self._metric_month_start.month

    @property
    def metric_year(self) -> int:
        return self._metric_month_start.year

    @property
    def metric_months(self) -> List[Tuple[int, int]]:
        return [(metric_month.year, metric_month.month) for metric_month in self._metric_months]

    @property
    def overflow_month(self) -> int:
        return self._overflow_month_start.month

    @property
    def overflow_year(self) -> int:
        return self._overflow_month_start.year

    def contains(self, time: datetime):
        return self._metric_month_start <= time < self._overflow_month_start
