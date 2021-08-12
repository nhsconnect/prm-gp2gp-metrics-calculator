from typing import List

from prmcalculator.domain.gp2gp.transfer import Transfer, filter_for_successful_transfers
from prmcalculator.domain.ods_portal.organisation_metadata import OrganisationMetadata
from prmcalculator.domain.practice.metrics_calculator import calculate_monthly_sla_by_practice
from prmcalculator.domain.practice.metrics_presentation import (
    PracticeMetricsPresentation,
    construct_practice_summaries,
    construct_practice_metrics_presentation,
)
from prmcalculator.domain.practice.practice_lookup import PracticeLookup
from prmcalculator.utils.reporting_window import MonthlyReportingWindow


def calculate_practice_metrics_data(
    transfers: List[Transfer],
    organisation_metadata: OrganisationMetadata,
    reporting_window: MonthlyReportingWindow,
) -> PracticeMetricsPresentation:
    completed_transfers = filter_for_successful_transfers(transfers)
    practice_lookup = PracticeLookup(organisation_metadata.practices)
    sla_metrics = calculate_monthly_sla_by_practice(
        practice_lookup, completed_transfers, reporting_window
    )
    practice_summaries = construct_practice_summaries(sla_metrics)
    practice_metrics_presentation = construct_practice_metrics_presentation(
        practice_summaries, organisation_metadata.ccgs
    )
    return practice_metrics_presentation
