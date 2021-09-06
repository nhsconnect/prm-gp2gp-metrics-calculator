from dataclasses import dataclass
from typing import List

from prmcalculator.domain.ods_portal.organisation_metadata import PracticeDetails
from prmcalculator.domain.practice.practice_transfer_metrics import PracticeTransferMetrics
from prmcalculator.domain.practice.transfer_metrics import TransferMetrics
from prmcalculator.utils.reporting_window import MonthlyReportingWindow


@dataclass
class TransfersIntegrated:
    count: int


@dataclass
class TransfersReceived:
    count: int
    transfers_integrated: TransfersIntegrated


@dataclass
class TransfersRequested:
    transfers_received: TransfersReceived


@dataclass
class RequesterMetrics:
    transfers_requested: TransfersRequested


@dataclass
class RequestedTransferMetrics:
    requested_count: int
    received_count: int


@dataclass
class MonthlyMetricsPresentation:
    year: int
    month: int
    requester: RequesterMetrics
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
        ),
        requester=RequesterMetrics(
            transfers_requested=TransfersRequested(
                transfers_received=TransfersReceived(
                    count=transfer_month_metrics.received_by_practice_total(),
                    transfers_integrated=TransfersIntegrated(
                        count=transfer_month_metrics.integrated_total()
                    ),
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
