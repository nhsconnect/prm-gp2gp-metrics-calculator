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
class OutcomeMetrics:
    total: int


@dataclass
class TransferOutcomesPresentation:
    technical_failure: OutcomeMetrics


@dataclass
class NationalMetricsPresentation:
    generated_on: datetime
    national_metrics_months: List[NationalMetricsMonth]
    transfer_outcomes: TransferOutcomesPresentation

    @property
    def metrics(self) -> List[NationalMetricMonthPresentation]:
        return [
            NationalMetricMonthPresentation(
                year=self.national_metrics_months[0].year,
                month=self.national_metrics_months[0].month,
            )
        ]


def construct_national_metrics_presentation(national_metrics_months: List[NationalMetricsMonth]):
    transfer_outcomes_month = national_metrics_months[0].transfer_outcomes

    return NationalMetricsPresentation(
        generated_on=datetime.now(tzutc()),
        national_metrics_months=national_metrics_months,
        transfer_outcomes=TransferOutcomesPresentation(
            technical_failure=OutcomeMetrics(total=transfer_outcomes_month.technical_failure.total)
        ),
    )
