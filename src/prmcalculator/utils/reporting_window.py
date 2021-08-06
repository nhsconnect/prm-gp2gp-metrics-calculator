from datetime import datetime
from typing import Tuple, List

from dateutil.relativedelta import relativedelta
from dateutil.tz import tzutc


class MonthlyReportingWindow:
    @classmethod
    def prior_to(cls, date_anchor: datetime, number_of_months: int):
        date_anchor_month_start = datetime(date_anchor.year, date_anchor.month, 1, tzinfo=tzutc())
        metric_monthly_datetimes = [
            date_anchor_month_start - relativedelta(months=number + 1)
            for number in range(number_of_months)
        ]
        return cls(date_anchor_month_start, metric_monthly_datetimes)

    def __init__(
        self,
        date_anchor_month_start: datetime,
        metric_monthly_datetimes: List[datetime],
    ):
        self._date_anchor_month_start = date_anchor_month_start
        self._metric_monthly_datetimes = metric_monthly_datetimes
        self._latest_metric_month = metric_monthly_datetimes[0]

    @property
    def metric_month(self) -> int:
        return self._latest_metric_month.month

    @property
    def metric_year(self) -> int:
        return self._latest_metric_month.year

    @property
    def metric_months(self) -> List[Tuple[int, int]]:
        return [
            (metric_month.year, metric_month.month)
            for metric_month in self._metric_monthly_datetimes
        ]

    @property
    def date_anchor_month(self) -> int:
        return self._date_anchor_month_start.month

    @property
    def date_anchor_year(self) -> int:
        return self._date_anchor_month_start.year

    def contains(self, time: datetime):
        return self._latest_metric_month <= time < self._date_anchor_month_start
