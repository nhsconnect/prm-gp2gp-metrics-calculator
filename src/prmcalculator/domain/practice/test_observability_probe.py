from unittest.mock import Mock

from prmcalculator.domain.practice.calculate_practice_metrics_data import (
    PracticeMetricsObservabilityProbe,
)
from prmcalculator.utils.reporting_window import MonthlyReportingWindow
from tests.builders.common import a_datetime


def test_probe_should_log_event_when_calculating_practice_metrics():
    mock_logger = Mock()
    probe = PracticeMetricsObservabilityProbe(mock_logger)

    date_anchor = a_datetime(year=2021, month=8)
    reporting_window = MonthlyReportingWindow.prior_to(date_anchor=date_anchor, number_of_months=3)

    probe.record_calculating_practice_metrics(reporting_window)

    mock_logger.info.assert_called_once_with(
        "Calculating practice metrics",
        extra={
            "event": "CALCULATING_PRACTICE_METRICS",
            "metric_months": [(2021, 7), (2021, 6), (2021, 5)],
        },
    )
