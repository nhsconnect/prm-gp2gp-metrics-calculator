from dataclasses import dataclass
from datetime import datetime
from typing import List, Dict

from dateutil.tz import tzutc

from prmcalculator.domain.gp2gp.transfer import Transfer
from prmcalculator.domain.ods_portal.organisation_metadata import CcgDetails, OrganisationMetadata
from prmcalculator.domain.practice.construct_practice_summary_v5 import (
    construct_practice_summary,
    PracticeSummary,
)
from prmcalculator.domain.practice.group_transfers_by_practice import (
    group_transfers_by_practice,
)
from prmcalculator.domain.practice.practice_lookup import PracticeLookup
from prmcalculator.domain.practice.practice_transfer_metrics import PracticeTransferMetrics
from prmcalculator.utils.reporting_window import MonthlyReportingWindow

from logging import getLogger, Logger

module_logger = getLogger(__name__)


class PracticeMetricsObservabilityProbe:
    def __init__(self, logger: Logger = module_logger):
        self._logger = logger

    def record_calculating_practice_metrics(self, reporting_window: MonthlyReportingWindow):
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


def calculate_practice_metrics_data(
    transfers: List[Transfer],
    organisation_metadata: OrganisationMetadata,
    reporting_window: MonthlyReportingWindow,
    observability_probe: PracticeMetricsObservabilityProbe,
) -> PracticeMetricsPresentation:
    observability_probe.record_calculating_practice_metrics(reporting_window)
    practice_lookup = PracticeLookup(organisation_metadata.practices)
    practice_transfers = group_transfers_by_practice(
        transfers=transfers,
        practice_lookup=practice_lookup,
        observability_probe=observability_probe,
    )
    practice_transfer_metrics = _create_practice_transfer_metrics_mapping(practice_transfers)

    return PracticeMetricsPresentation(
        generated_on=datetime.now(tzutc()),
        practices=[
            construct_practice_summary(
                practice_details=practice_details,
                practice_metrics=practice_transfer_metrics[practice_details.ods_code],
                reporting_window=reporting_window,
            )
            for practice_details in practice_lookup.all_practices()
        ],
        ccgs=organisation_metadata.ccgs,
    )


def _create_practice_transfer_metrics_mapping(
    practice_transfers: Dict[str, List[Transfer]],
) -> Dict[str, PracticeTransferMetrics]:
    return {
        ods_code: PracticeTransferMetrics(transfers)
        for (ods_code, transfers) in practice_transfers.items()
    }
