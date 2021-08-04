from typing import List

from prmcalculator.domain.national.metrics_calculator import calculate_national_metrics
from prmcalculator.domain.national.metrics_presentation import (
    NationalMetricsPresentation,
    construct_national_metrics,
)
from prmcalculator.domain.practice.metrics_presentation import (
    construct_practice_summaries,
    PracticeMetricsPresentation,
    construct_practice_metrics_presentation,
)
from prmcalculator.domain.practice.practice_lookup import PracticeLookup
from prmcalculator.domain.ods_portal.organisation_metadata import OrganisationMetadata
from prmcalculator.domain.gp2gp.transfer import (
    Transfer,
    filter_for_successful_transfers,
    filter_transfers_by_date_requested,
)
from prmcalculator.domain.practice.metrics_calculator import calculate_monthly_sla_by_practice

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
    practice_summaries = construct_practice_summaries(
        sla_metrics, year=reporting_window.metric_year, month=reporting_window.metric_month
    )
    practice_metrics_presentation = construct_practice_metrics_presentation(
        practice_summaries, organisation_metadata.ccgs
    )
    return practice_metrics_presentation


def calculate_national_metrics_data(
    transfers: List[Transfer], reporting_window: MonthlyReportingWindow
) -> NationalMetricsPresentation:
    metric_month_transfers = filter_transfers_by_date_requested(transfers, reporting_window)
    national_metrics = calculate_national_metrics(transfers=metric_month_transfers)
    return construct_national_metrics(
        national_metrics=national_metrics,
        year=reporting_window.metric_year,
        month=reporting_window.metric_month,
    )
