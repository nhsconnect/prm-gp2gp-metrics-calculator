from dataclasses import dataclass
from datetime import datetime
from typing import List

from dateutil.tz import tzutc

from prmcalculator.domain.national.metrics_calculator_deprecated import NationalMetricsDeprecated
from prmcalculator.utils.calculate_percentage import calculate_percentage


@dataclass
class PaperFallbackMetricsDeprecated:
    transfer_count: int
    transfer_percentage: float


@dataclass
class FailedMetricsDeprecated:
    transfer_count: int
    transfer_percentage: float


@dataclass
class PendingMetricsDeprecated:
    transfer_count: int
    transfer_percentage: float


@dataclass
class IntegratedMetricsPresentationDeprecated:
    transfer_count: int
    transfer_percentage: float
    within_3_days: int
    within_8_days: int
    beyond_8_days: int


@dataclass
class MonthlyNationalMetricsDeprecated:
    transfer_count: int
    integrated: IntegratedMetricsPresentationDeprecated
    failed: FailedMetricsDeprecated
    pending: PendingMetricsDeprecated
    paper_fallback: PaperFallbackMetricsDeprecated
    year: int
    month: int


@dataclass
class NationalMetricsPresentationDeprecated:
    generated_on: datetime
    metrics: List[MonthlyNationalMetricsDeprecated]


def _construct_integrated_metrics(
    national_metrics: NationalMetricsDeprecated,
) -> IntegratedMetricsPresentationDeprecated:
    return IntegratedMetricsPresentationDeprecated(
        transfer_percentage=calculate_percentage(
            portion=national_metrics.integrated.transfer_count,
            total=national_metrics.initiated_transfer_count,
            num_digits=2,
        ),
        transfer_count=national_metrics.integrated.transfer_count,
        within_3_days=national_metrics.integrated.within_3_days,
        within_8_days=national_metrics.integrated.within_8_days,
        beyond_8_days=national_metrics.integrated.beyond_8_days,
    )


def _construct_failed_metrics(
    national_metrics: NationalMetricsDeprecated,
) -> FailedMetricsDeprecated:
    return FailedMetricsDeprecated(
        transfer_count=national_metrics.failed_transfer_count,
        transfer_percentage=calculate_percentage(
            portion=national_metrics.failed_transfer_count,
            total=national_metrics.initiated_transfer_count,
            num_digits=2,
        ),
    )


def _construct_pending_metrics(
    national_metrics: NationalMetricsDeprecated,
) -> PendingMetricsDeprecated:
    return PendingMetricsDeprecated(
        transfer_count=national_metrics.pending_transfer_count,
        transfer_percentage=calculate_percentage(
            portion=national_metrics.pending_transfer_count,
            total=national_metrics.initiated_transfer_count,
            num_digits=2,
        ),
    )


def _construct_paper_fallback_metrics(
    national_metrics: NationalMetricsDeprecated,
) -> PaperFallbackMetricsDeprecated:
    paper_fallback_count = national_metrics.calculate_paper_fallback()

    return PaperFallbackMetricsDeprecated(
        transfer_count=paper_fallback_count,
        transfer_percentage=calculate_percentage(
            portion=paper_fallback_count,
            total=national_metrics.initiated_transfer_count,
            num_digits=2,
        ),
    )


def construct_national_metrics_deprecated(
    national_metrics: NationalMetricsDeprecated,
    year: int,
    month: int,
) -> NationalMetricsPresentationDeprecated:
    current_datetime = datetime.now(tzutc())

    return NationalMetricsPresentationDeprecated(
        generated_on=current_datetime,
        metrics=[
            MonthlyNationalMetricsDeprecated(
                transfer_count=national_metrics.initiated_transfer_count,
                integrated=_construct_integrated_metrics(national_metrics),
                failed=_construct_failed_metrics(national_metrics),
                pending=_construct_pending_metrics(national_metrics),
                paper_fallback=_construct_paper_fallback_metrics(national_metrics),
                year=year,
                month=month,
            )
        ],
    )
