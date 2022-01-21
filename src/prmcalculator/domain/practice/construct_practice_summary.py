from dataclasses import dataclass
from typing import List

from prmcalculator.domain.monthly_reporting_window import MonthlyReportingWindow
from prmcalculator.domain.practice.practice_transfer_metrics import PracticeTransferMetrics
from prmcalculator.domain.practice.transfer_metrics import TransferMetrics


@dataclass
class RequestedTransferMetrics:
    requested_count: int
    received_count: int
    integrated_count: int
    integrated_within_3_days_count: int
    integrated_within_8_days_count: int
    integrated_beyond_8_days_count: int
    awaiting_integration_count: int
    technical_failures_count: int
    unclassified_failure_count: int


@dataclass
class MonthlyMetricsPresentation:
    year: int
    month: int
    requested_transfers: RequestedTransferMetrics


@dataclass
class PracticeSummary:
    name: str
    ods_code: str
    metrics: List[MonthlyMetricsPresentation]


def _construct_monthly_metrics_presentation(
    transfer_month_metrics: TransferMetrics, year: int, month: int
) -> MonthlyMetricsPresentation:

    return MonthlyMetricsPresentation(
        year=year,
        month=month,
        requested_transfers=RequestedTransferMetrics(
            requested_count=transfer_month_metrics.requested_by_practice_total(),
            received_count=transfer_month_metrics.received_by_practice_total(),
            integrated_count=transfer_month_metrics.integrated_total(),
            integrated_within_3_days_count=transfer_month_metrics.integrated_within_3_days(),
            integrated_within_8_days_count=transfer_month_metrics.integrated_within_8_days(),
            integrated_beyond_8_days_count=transfer_month_metrics.integrated_beyond_8_days(),
            awaiting_integration_count=transfer_month_metrics.process_failure_not_integrated(),
            technical_failures_count=transfer_month_metrics.technical_failures_total(),
            unclassified_failure_count=transfer_month_metrics.unclassified_failure_total(),
        ),
    )


def construct_practice_summary(
    practice_metrics: PracticeTransferMetrics,
    reporting_window: MonthlyReportingWindow,
) -> PracticeSummary:
    return PracticeSummary(
        name=practice_metrics.name,
        ods_code=practice_metrics.ods_code,
        metrics=[
            _construct_monthly_metrics_presentation(
                transfer_month_metrics=practice_metrics.monthly_metrics(year=year, month=month),
                year=year,
                month=month,
            )
            for (year, month) in reporting_window.metric_months
        ],
    )
