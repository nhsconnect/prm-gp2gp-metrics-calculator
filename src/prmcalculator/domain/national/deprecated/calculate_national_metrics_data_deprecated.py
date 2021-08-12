from typing import List

from prmcalculator.domain.gp2gp.transfer import Transfer, filter_transfers_by_date_requested
from prmcalculator.domain.national.deprecated.metrics_calculator_deprecated import (
    calculate_national_metrics_deprecated,
)
from prmcalculator.domain.national.deprecated.metrics_presentation_deprecated import (
    NationalMetricsPresentationDeprecated,
    construct_national_metrics_deprecated,
)
from prmcalculator.utils.reporting_window import MonthlyReportingWindow


def calculate_national_metrics_data_deprecated(
    transfers: List[Transfer], reporting_window: MonthlyReportingWindow
) -> NationalMetricsPresentationDeprecated:
    metric_month_transfers = filter_transfers_by_date_requested(transfers, reporting_window)
    national_metrics = calculate_national_metrics_deprecated(transfers=metric_month_transfers)
    return construct_national_metrics_deprecated(
        national_metrics=national_metrics,
        year=reporting_window.metric_year,
        month=reporting_window.metric_month,
    )
