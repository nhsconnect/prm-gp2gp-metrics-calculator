from dataclasses import dataclass
from typing import List

from prmcalculator.domain.ods_portal.organisation_metadata import PracticeDetails
from prmcalculator.domain.practice.practice_transfer_metrics import PracticeTransferMetrics
from prmcalculator.domain.practice.transfer_metrics import TransferMetrics
from prmcalculator.utils.reporting_window import MonthlyReportingWindow


@dataclass
class TransfersReceivedPresentation:
    count: int


@dataclass
class TransfersRequestedPresentation:
    count: int
    transfers_received: TransfersReceivedPresentation


@dataclass
class RequesterMetrics:
    transfers_requested: TransfersRequestedPresentation


@dataclass
class MonthlyMetricsPresentation:
    year: int
    month: int
    requester: RequesterMetrics


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
        requester=RequesterMetrics(
            transfers_requested=TransfersRequestedPresentation(
                count=transfer_month_metrics.requested_by_practice_total(),
                transfers_received=TransfersReceivedPresentation(
                    count=transfer_month_metrics.received_by_practice_total()
                ),
            )
        ),
    )


def construct_practice_summary(
    practice_details: PracticeDetails,
    practice_metrics: PracticeTransferMetrics,
    reporting_window: MonthlyReportingWindow,
) -> PracticeSummary:
    latest_year = reporting_window.metric_months[0][0]
    latest_month = reporting_window.metric_months[0][1]

    return PracticeSummary(
        name=practice_details.name,
        ods_code=practice_details.ods_code,
        metrics=[
            _construct_monthly_metrics_presentation(
                transfer_month_metrics=practice_metrics.monthly_metrics(latest_year, latest_month),
                year=latest_year,
                month=latest_month,
            )
        ],
    )
