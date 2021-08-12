from dataclasses import dataclass
from datetime import datetime
from typing import List

from dateutil.tz import tzutc

from prmcalculator.domain.gp2gp.transfer import TransferFailureReason
from prmcalculator.domain.national.calculate_national_metrics_month import NationalMetricsMonth
from prmcalculator.domain.national.transfer_outcomes import TransferOutcomes
from prmcalculator.utils.calculate_percentage import calculate_percentage


@dataclass
class OutcomeMetricsPresentation:
    total: int
    percent: float


@dataclass
class ProcessFailureMetricsPresentation(OutcomeMetricsPresentation):
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

    total_number_of_transfers_month = national_metric_month.total

    return NationalMetricsPresentation(
        generated_on=datetime.now(tzutc()),
        metrics=[
            NationalMetricMonthPresentation(
                year=national_metric_month.year,
                month=national_metric_month.month,
                total=total_number_of_transfers_month,
                transfer_outcomes=TransferOutcomesPresentation(
                    integrated_on_time=OutcomeMetricsPresentation(
                        total=transfer_outcomes_month.integrated_on_time.total,
                        percent=calculate_percentage(
                            portion=transfer_outcomes_month.integrated_on_time.total,
                            total=total_number_of_transfers_month,
                            num_digits=2,
                        ),
                    ),
                    process_failure=_construct_process_failure_metrics(
                        total_number_of_transfers_month, transfer_outcomes_month
                    ),
                    technical_failure=OutcomeMetricsPresentation(
                        total=transfer_outcomes_month.technical_failure.total,
                        percent=calculate_percentage(
                            portion=transfer_outcomes_month.technical_failure.total,
                            total=total_number_of_transfers_month,
                            num_digits=2,
                        ),
                    ),
                    unclassified_failure=OutcomeMetricsPresentation(
                        total=transfer_outcomes_month.unclassified_failure.total,
                        percent=calculate_percentage(
                            portion=transfer_outcomes_month.unclassified_failure.total,
                            total=total_number_of_transfers_month,
                            num_digits=2,
                        ),
                    ),
                ),
            )
        ],
    )


def _construct_process_failure_metrics(
    total_number_of_transfers_month: int, transfer_outcomes_month: TransferOutcomes
) -> ProcessFailureMetricsPresentation:
    transferred_not_integrated_total = transfer_outcomes_month.process_failure.failure_reason(
        TransferFailureReason.TRANSFERRED_NOT_INTEGRATED
    ).total

    integrated_late_total = transfer_outcomes_month.process_failure.failure_reason(
        TransferFailureReason.INTEGRATED_LATE
    ).total

    return ProcessFailureMetricsPresentation(
        total=transfer_outcomes_month.process_failure.total,
        percent=calculate_percentage(
            portion=transfer_outcomes_month.process_failure.total,
            total=total_number_of_transfers_month,
            num_digits=2,
        ),
        integrated_late=OutcomeMetricsPresentation(
            total=integrated_late_total,
            percent=calculate_percentage(
                portion=integrated_late_total,
                total=total_number_of_transfers_month,
                num_digits=2,
            ),
        ),
        transferred_not_integrated=OutcomeMetricsPresentation(
            total=transferred_not_integrated_total,
            percent=calculate_percentage(
                portion=transferred_not_integrated_total,
                total=total_number_of_transfers_month,
                num_digits=2,
            ),
        ),
    )
