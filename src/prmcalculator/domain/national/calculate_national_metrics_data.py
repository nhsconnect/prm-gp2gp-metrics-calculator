from typing import List

from prmcalculator.domain.gp2gp.transfer import Transfer, filter_transfers_by_date_requested
from prmcalculator.domain.national.calculate_national_metrics_month import NationalMetricsMonth
from prmcalculator.domain.national.construct_national_metrics_presentation import (
    construct_national_metrics_presentation,
    NationalMetricsPresentation,
)
from prmcalculator.utils.reporting_window import MonthlyReportingWindow


def calculate_national_metrics_data(
    transfers: List[Transfer], reporting_window: MonthlyReportingWindow
) -> NationalMetricsPresentation:
    metric_month_transfers = filter_transfers_by_date_requested(transfers, reporting_window)
    national_metrics = NationalMetricsMonth(
        transfers=metric_month_transfers,
        year=reporting_window.metric_year,
        month=reporting_window.metric_month,
    )
    return construct_national_metrics_presentation(
        national_metrics_months=[national_metrics],
    )
