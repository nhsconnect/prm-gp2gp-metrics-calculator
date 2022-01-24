from dataclasses import dataclass
from datetime import datetime, timedelta
from logging import Logger, getLogger
from typing import List, Optional, Union

from dateutil.tz import tzutc

from prmcalculator.domain.gp2gp.transfer import Transfer
from prmcalculator.domain.monthly_reporting_window import MonthlyReportingWindow
from prmcalculator.domain.ods_portal.organisation_metadata import CcgDetails, OrganisationMetadata
from prmcalculator.domain.practice.construct_practice_summary import (
    PracticeSummary,
    construct_practice_summary,
)
from prmcalculator.domain.practice.group_transfers_by_practice import group_transfers_by_practice
from prmcalculator.domain.practice.practice_lookup import PracticeLookup
from prmcalculator.domain.practice.practice_transfer_metrics import PracticeTransferMetrics
from prmcalculator.domain.reporting_window import ReportingWindow

module_logger = getLogger(__name__)


class PracticeMetricsObservabilityProbe:
    def __init__(self, logger: Logger = module_logger):
        self._logger = logger

    def record_calculating_practice_metrics(
        self, reporting_window: Union[MonthlyReportingWindow, ReportingWindow]
    ):
        self._logger.info(
            "Calculating practice metrics",
            extra={
                "event": "CALCULATING_PRACTICE_METRICS",
                "metric_months": reporting_window.metric_months,
            },
        )

    def record_unknown_practice_for_transfer(self, transfer: Transfer):
        self._logger.warning(
            "Unknown practice for transfer",
            extra={
                "event": "UNKNOWN_PRACTICE_FOR_TRANSFER",
                "conversation_id": transfer.conversation_id,
                "unknown_asid": transfer.requesting_practice.asid,
            },
        )


@dataclass
class PracticeMetricsPresentation:
    generated_on: datetime
    practices: List[PracticeSummary]
    ccgs: List[CcgDetails]


def calculate_practice_metrics(
    transfers: List[Transfer],
    organisation_metadata: OrganisationMetadata,
    reporting_window: Union[MonthlyReportingWindow, ReportingWindow],
    observability_probe: PracticeMetricsObservabilityProbe,
    hide_slow_transferred_records_after_days: Optional[int] = None,
) -> PracticeMetricsPresentation:
    observability_probe.record_calculating_practice_metrics(reporting_window)
    practice_lookup = PracticeLookup(organisation_metadata.practices)

    transfers = (
        _filter_out_slow_transfers(transfers, hide_slow_transferred_records_after_days)
        if hide_slow_transferred_records_after_days
        else transfers
    )

    grouped_transfers = group_transfers_by_practice(
        transfers=transfers,
        practice_lookup=practice_lookup,
        observability_probe=observability_probe,
    )

    return PracticeMetricsPresentation(
        generated_on=datetime.now(tzutc()),
        practices=[
            construct_practice_summary(
                practice_metrics=PracticeTransferMetrics.from_group(practice_transfers),
                reporting_window=reporting_window,
            )
            for practice_transfers in grouped_transfers
        ],
        ccgs=organisation_metadata.ccgs,
    )


def _filter_out_slow_transfers(
    transfers: List[Transfer], hide_slow_transferred_records_after_days: int
) -> List[Transfer]:
    filtered_transfers = []

    for transfer in transfers:

        if transfer.last_sender_message_timestamp is None:
            filtered_transfers.append(transfer)

        else:
            allowed_time_for_transfer = transfer.date_requested + timedelta(
                hide_slow_transferred_records_after_days
            )
            if allowed_time_for_transfer > transfer.last_sender_message_timestamp:
                filtered_transfers.append(transfer)

    return filtered_transfers
