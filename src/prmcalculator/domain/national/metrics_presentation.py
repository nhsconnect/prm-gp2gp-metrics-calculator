from dataclasses import dataclass
from datetime import datetime
from typing import List

from dateutil.tz import tzutc

from prmcalculator.domain.national.metrics_calculator import NationalMetricsMonth


@dataclass
class NationalMetricMonthPresentation:
    year: int
    month: int


@dataclass
class NationalMetricsPresentation:
    generated_on: datetime
    national_metrics_months: List[NationalMetricsMonth]

    @property
    def metrics(self) -> List[NationalMetricMonthPresentation]:
        return [
            NationalMetricMonthPresentation(
                year=self.national_metrics_months[0].year,
                month=self.national_metrics_months[0].month,
            )
        ]


def construct_national_metrics_presentation(national_metrics_months: List[NationalMetricsMonth]):
    current_date = datetime.now(tzutc())
    return NationalMetricsPresentation(
        generated_on=current_date, national_metrics_months=national_metrics_months
    )
