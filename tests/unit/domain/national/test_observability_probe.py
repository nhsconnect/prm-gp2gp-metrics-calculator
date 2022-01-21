from unittest.mock import Mock

from prmcalculator.domain.monthly_reporting_window import MonthlyReportingWindow
from prmcalculator.domain.national.calculate_national_metrics_data import (
    NationalMetricsObservabilityProbe,
)
from tests.builders.common import a_datetime


def test_probe_should_log_event_when_calculating_national_metrics():
    mock_logger = Mock()
    probe = NationalMetricsObservabilityProbe(mock_logger)

    date_anchor = a_datetime(year=2021, month=8)
    reporting_window = MonthlyReportingWindow.prior_to(date_anchor=date_anchor, number_of_months=3)

    probe.record_calculating_national_metrics(reporting_window)

    mock_logger.info.assert_called_once_with(
        "Calculating national metrics",
        extra={"event": "CALCULATING_NATIONAL_METRICS", "metric_month": (2021, 7)},
    )
