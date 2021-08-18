from typing import List

from prmcalculator.domain.gp2gp.transfer import Transfer, filter_for_successful_transfers
from prmcalculator.domain.ods_portal.organisation_metadata import OrganisationMetadata
from prmcalculator.domain.practice.deprecated.metrics_calculator_deprecated import (
    calculate_monthly_sla_by_practice_deprecated,
)
from prmcalculator.domain.practice.deprecated.metrics_presentation_deprecated import (
    PracticeMetricsPresentationDeprecated,
    construct_practice_summaries_deprecated,
    construct_practice_metrics_presentation_deprecated,
)
from prmcalculator.domain.practice.practice_lookup import PracticeLookup
from prmcalculator.utils.reporting_window import MonthlyReportingWindow


def calculate_practice_metrics_data_deprecated(
    transfers: List[Transfer],
    organisation_metadata: OrganisationMetadata,
    reporting_window: MonthlyReportingWindow,
) -> PracticeMetricsPresentationDeprecated:
    completed_transfers = filter_for_successful_transfers(transfers)
    practice_lookup = PracticeLookup(organisation_metadata.practices)
    sla_metrics = calculate_monthly_sla_by_practice_deprecated(
        practice_lookup, completed_transfers, reporting_window
    )
    practice_summaries = construct_practice_summaries_deprecated(sla_metrics)
    practice_metrics_presentation = construct_practice_metrics_presentation_deprecated(
        practice_summaries, organisation_metadata.ccgs
    )
    return practice_metrics_presentation
