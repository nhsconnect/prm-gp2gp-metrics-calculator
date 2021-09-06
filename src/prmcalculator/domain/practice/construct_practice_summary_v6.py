from dataclasses import dataclass
from typing import List

from prmcalculator.domain.practice.practice_transfer_metrics import PracticeTransferMetrics
from prmcalculator.domain.practice.transfer_metrics import TransferMetrics
from prmcalculator.utils.reporting_window import MonthlyReportingWindow


@dataclass
class RequestedTransferMetrics:
    requested_count: int
    received_count: int
    integrated_count: int
    integrated_within_3_days_count: int
    integrated_within_8_days_count: int
    integrated_beyond_8_days_count: int


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
        ),
    )


def construct_practice_summary(
    practice_metrics: PracticeTransferMetrics,
    reporting_window: MonthlyReportingWindow,
) -> PracticeSummary:
    latest_year = reporting_window.metric_months[0][0]
    latest_month = reporting_window.metric_months[0][1]

    return PracticeSummary(
        name=practice_metrics.name,
        ods_code=practice_metrics.ods_code,
        metrics=[
            _construct_monthly_metrics_presentation(
                transfer_month_metrics=practice_metrics.monthly_metrics(latest_year, latest_month),
                year=latest_year,
                month=latest_month,
            )
        ],
    )
