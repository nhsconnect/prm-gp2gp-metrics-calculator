from unittest.mock import Mock

from prmcalculator.domain.practice.construct_practice_summary import (
    MonthlyMetricsPresentation,
    PracticeSummary,
    RequestedTransferMetrics,
    construct_practice_summary,
)
from prmcalculator.domain.reporting_window import ReportingWindow
from tests.builders.common import a_datetime


def test_returns_a_practice_summary_for_one_month_of_metrics():
    mock_transfer_metrics = Mock()
    mock_transfer_metrics.ods_code = "ABC123"
    mock_transfer_metrics.name = "Test Practice"
    mock_monthly_metrics = Mock()
    mock_transfer_metrics.monthly_metrics.return_value = mock_monthly_metrics
    mock_monthly_metrics.requested_by_practice_total.return_value = 1
    mock_monthly_metrics.received_by_practice_total.return_value = 2
    mock_monthly_metrics.integrated_total.return_value = 3
    mock_monthly_metrics.integrated_within_3_days.return_value = 4
    mock_monthly_metrics.integrated_within_8_days.return_value = 5
    mock_monthly_metrics.integrated_beyond_8_days.return_value = 6
    mock_monthly_metrics.process_failure_not_integrated.return_value = 7
    mock_monthly_metrics.technical_failures_total.return_value = 8
    mock_monthly_metrics.unclassified_failure_total.return_value = 9

    reporting_window = ReportingWindow.prior_to(a_datetime(year=2021, month=7), number_of_months=1)

    expected = PracticeSummary(
        ods_code="ABC123",
        name="Test Practice",
        metrics=[
            MonthlyMetricsPresentation(
                year=2021,
                month=6,
                requested_transfers=RequestedTransferMetrics(
                    requested_count=1,
                    received_count=2,
                    integrated_count=3,
                    integrated_within_3_days_count=4,
                    integrated_within_8_days_count=5,
                    integrated_beyond_8_days_count=6,
                    awaiting_integration_count=7,
                    technical_failures_count=8,
                    unclassified_failure_count=9,
                ),
            )
        ],
    )

    actual = construct_practice_summary(
        practice_metrics=mock_transfer_metrics,
        reporting_window=reporting_window,
    )

    assert actual == expected


def test_returns_a_practice_summary_for_multiple_months():
    mock_transfer_metrics = Mock()
    mock_transfer_metrics.monthly_metrics.return_value = Mock()

    reporting_window = ReportingWindow.prior_to(a_datetime(year=2021, month=7), number_of_months=3)

    actual = construct_practice_summary(
        practice_metrics=mock_transfer_metrics,
        reporting_window=reporting_window,
    )

    assert actual.metrics[0].month == 6
    assert actual.metrics[1].month == 5
    assert actual.metrics[2].month == 4
    mock_transfer_metrics.monthly_metrics.assert_any_call(year=2021, month=6)
    mock_transfer_metrics.monthly_metrics.assert_any_call(year=2021, month=5)
    mock_transfer_metrics.monthly_metrics.assert_any_call(year=2021, month=4)
    assert mock_transfer_metrics.monthly_metrics.call_count == 3
