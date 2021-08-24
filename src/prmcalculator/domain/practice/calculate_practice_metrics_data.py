from dataclasses import dataclass
from datetime import datetime
from typing import List, Dict

from dateutil.tz import tzutc

from prmcalculator.domain.gp2gp.transfer import Transfer
from prmcalculator.domain.ods_portal.organisation_metadata import CcgDetails, OrganisationMetadata
from prmcalculator.domain.practice.construct_practice_summary import (
    construct_practice_summary,
    PracticeSummary,
)
from prmcalculator.domain.practice.create_practice_transfer_mapping import (
    create_practice_transfer_mapping,
)
from prmcalculator.domain.practice.practice_lookup import PracticeLookup
from prmcalculator.domain.practice.practice_transfer_metrics import PracticeTransferMetrics
from prmcalculator.utils.reporting_window import MonthlyReportingWindow


@dataclass
class PracticeMetricsPresentation:
    generated_on: datetime
    practices: List[PracticeSummary]
    ccgs: List[CcgDetails]


def calculate_practice_metrics_data(
    transfers: List[Transfer],
    organisation_metadata: OrganisationMetadata,
    reporting_window: MonthlyReportingWindow,
) -> PracticeMetricsPresentation:
    practice_lookup = PracticeLookup(organisation_metadata.practices)
    practice_transfers = create_practice_transfer_mapping(
        transfers=transfers, practice_lookup=practice_lookup
    )
    practice_transfer_metrics = _create_practice_transfer_metrics_mapping(practice_transfers)

    return PracticeMetricsPresentation(
        generated_on=datetime.now(tzutc()),
        practices=[
            construct_practice_summary(
                practice_metrics=practice_transfer_metrics[ods_code],
                reporting_window=reporting_window,
            )
            for ods_code in practice_lookup.all_ods_codes()
        ],
        ccgs=organisation_metadata.ccgs,
    )


def _create_practice_transfer_metrics_mapping(
    practice_transfers: Dict[str, List[Transfer]]
) -> Dict[str, PracticeTransferMetrics]:
    practice_transfer_metrics = {}

    for practice_ods_code in practice_transfers.keys():
        transfers = practice_transfers[practice_ods_code]
        practice_transfer_metrics[practice_ods_code] = PracticeTransferMetrics(
            ods_code=practice_ods_code, transfers=transfers
        )
    return practice_transfer_metrics
