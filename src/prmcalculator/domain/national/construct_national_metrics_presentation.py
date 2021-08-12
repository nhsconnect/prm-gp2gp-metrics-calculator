from dataclasses import dataclass
from datetime import datetime
from typing import List

from dateutil.tz import tzutc

from prmcalculator.domain.gp2gp.transfer import TransferFailureReason
from prmcalculator.domain.national.calculate_national_metrics_month import NationalMetricsMonth


@dataclass
class OutcomeMetricsPresentation:
    total: int


@dataclass
class ProcessFailureMetricsPresentation:
    total: int
    integrated_late: OutcomeMetricsPresentation
    transferred_not_integrated: OutcomeMetricsPresentation


@dataclass
class TransferOutcomesPresentation:
    integrated_on_time: OutcomeMetricsPresentation
    technical_failure: OutcomeMetricsPresentation
    process_failure: ProcessFailureMetricsPresentation
    unclassified_failure: OutcomeMetricsPresentation


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
                    integrated_on_time=OutcomeMetricsPresentation(
                        total=transfer_outcomes_month.integrated_on_time.total
                    ),
                    process_failure=ProcessFailureMetricsPresentation(
                        total=transfer_outcomes_month.process_failure.total,
                        integrated_late=OutcomeMetricsPresentation(
                            total=transfer_outcomes_month.process_failure.count_by_failure_reason(
                                TransferFailureReason.INTEGRATED_LATE
                            )
                        ),
                        transferred_not_integrated=OutcomeMetricsPresentation(
                            total=transfer_outcomes_month.process_failure.count_by_failure_reason(
                                TransferFailureReason.TRANSFERRED_NOT_INTEGRATED
                            )
                        ),
                    ),
                    technical_failure=OutcomeMetricsPresentation(
                        total=transfer_outcomes_month.technical_failure.total
                    ),
                    unclassified_failure=OutcomeMetricsPresentation(
                        total=transfer_outcomes_month.unclassified_failure.total
                    ),
                ),
            )
        ],
    )
