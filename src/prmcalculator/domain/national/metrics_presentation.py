from dataclasses import dataclass
from datetime import datetime
from typing import List

from dateutil.tz import tzutc

from prmcalculator.domain.national.metrics_calculator import NationalMetricsMonth


@dataclass
class OutcomeMetricsPresentation:
    total: int


@dataclass
class TransferOutcomesPresentation:
    technical_failure: OutcomeMetricsPresentation


@dataclass
class NationalMetricMonthPresentation:
    year: int
    month: int
    total: int
    transfer_outcomes: TransferOutcomesPresentation


@dataclass
class NationalMetricsPresentation:
    generated_on: datetime
    metrics: List[NationalMetricMonthPresentation]


def construct_national_metrics_presentation(national_metrics_months: List[NationalMetricsMonth]):
    national_metric_month = national_metrics_months[0]
    transfer_outcomes_month = national_metric_month.transfer_outcomes

    return NationalMetricsPresentation(
        generated_on=datetime.now(tzutc()),
        metrics=[
            NationalMetricMonthPresentation(
                year=national_metric_month.year,
                month=national_metric_month.month,
                total=national_metric_month.total,
                transfer_outcomes=TransferOutcomesPresentation(
                    technical_failure=OutcomeMetricsPresentation(
                        total=transfer_outcomes_month.technical_failure.total
                    )
                ),
            )
        ],
    )
