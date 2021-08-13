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
    transfer_count: int
    transfer_percentage: float


@dataclass
class ProcessFailureMetricsPresentation:
    integrated_late: OutcomeMetricsPresentation
    transferred_not_integrated: OutcomeMetricsPresentation


@dataclass
class PaperFallbackMetricsPresentation(OutcomeMetricsPresentation):
    technical_failure: OutcomeMetricsPresentation
    process_failure: ProcessFailureMetricsPresentation
    unclassified_failure: OutcomeMetricsPresentation


@dataclass
class NationalMetricMonthPresentation:
    year: int
    month: int
    transfer_count: int
    integrated_on_time: OutcomeMetricsPresentation
    paper_fallback: PaperFallbackMetricsPresentation


@dataclass
class NationalMetricsPresentation:
    generated_on: datetime
    metrics: List[NationalMetricMonthPresentation]


def construct_national_metrics_presentation(
    national_metrics_months: List[NationalMetricsMonth],
) -> NationalMetricsPresentation:
    national_metric_month = national_metrics_months[0]
    transfer_outcomes_month = national_metric_month.transfer_outcomes

    total_number_of_transfers_month = national_metric_month.total

    return NationalMetricsPresentation(
        generated_on=datetime.now(tzutc()),
        metrics=[
            NationalMetricMonthPresentation(
                year=national_metric_month.year,
                month=national_metric_month.month,
                transfer_count=total_number_of_transfers_month,
                integrated_on_time=OutcomeMetricsPresentation(
                    transfer_count=transfer_outcomes_month.integrated_on_time.total,
                    transfer_percentage=calculate_percentage(
                        portion=transfer_outcomes_month.integrated_on_time.total,
                        total=total_number_of_transfers_month,
                    ),
                ),
                paper_fallback=_construct_paper_fallback_metrics(
                    total_number_of_transfers_month, transfer_outcomes_month
                ),
            )
        ],
    )


def _construct_paper_fallback_metrics(
    total_number_of_transfers_month: int, transfer_outcomes_month: TransferOutcomes
) -> PaperFallbackMetricsPresentation:
    paper_fallback_total = (
        total_number_of_transfers_month - transfer_outcomes_month.integrated_on_time.total
    )
    paper_fallback_percent = calculate_percentage(
        portion=paper_fallback_total, total=total_number_of_transfers_month
    )
    return PaperFallbackMetricsPresentation(
        transfer_count=paper_fallback_total,
        transfer_percentage=paper_fallback_percent,
        process_failure=_construct_process_failure_metrics(
            total_number_of_transfers_month, transfer_outcomes_month
        ),
        technical_failure=OutcomeMetricsPresentation(
            transfer_count=transfer_outcomes_month.technical_failure.total,
            transfer_percentage=calculate_percentage(
                portion=transfer_outcomes_month.technical_failure.total,
                total=total_number_of_transfers_month,
            ),
        ),
        unclassified_failure=OutcomeMetricsPresentation(
            transfer_count=transfer_outcomes_month.unclassified_failure.total,
            transfer_percentage=calculate_percentage(
                portion=transfer_outcomes_month.unclassified_failure.total,
                total=total_number_of_transfers_month,
            ),
        ),
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
        integrated_late=OutcomeMetricsPresentation(
            transfer_count=integrated_late_total,
            transfer_percentage=calculate_percentage(
                portion=integrated_late_total,
                total=total_number_of_transfers_month,
            ),
        ),
        transferred_not_integrated=OutcomeMetricsPresentation(
            transfer_count=transferred_not_integrated_total,
            transfer_percentage=calculate_percentage(
                portion=transferred_not_integrated_total,
                total=total_number_of_transfers_month,
            ),
        ),
    )
