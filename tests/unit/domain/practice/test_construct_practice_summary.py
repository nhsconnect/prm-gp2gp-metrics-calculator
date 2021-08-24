from prmcalculator.domain.practice.calculate_practice_metrics_data import construct_practice_summary
from prmcalculator.domain.practice.construct_practice_summary import (
    IntegratedPracticeMetricsPresentation,
    TransfersReceivedPresentation,
    AwaitingIntegration,
)

from prmcalculator.domain.practice.practice_transfer_metrics import PracticeTransferMetrics
from prmcalculator.utils.reporting_window import MonthlyReportingWindow
from tests.builders.common import a_datetime, a_string
from tests.builders.gp2gp import (
    build_transfer,
    a_transfer_integrated_within_3_days,
)


def test_returns_ods_code():
    expected_ods_code = "A12345"
    practice_transfer_metrics = PracticeTransferMetrics(
        ods_code=expected_ods_code,
        transfers=[build_transfer(date_requested=a_datetime(year=2021, month=7, day=4))],
    )
    reporting_window = MonthlyReportingWindow.prior_to(
        date_anchor=a_datetime(year=2021, month=8), number_of_months=1
    )

    actual = construct_practice_summary(
        practice_metrics=practice_transfer_metrics, reporting_window=reporting_window
    )

    assert actual.ods_code == expected_ods_code


def test_returns_year_and_month_for_first_metric():

    expected_year = 2019
    expected_month = 8

    practice_transfer_metrics = PracticeTransferMetrics(
        ods_code=a_string(),
        transfers=[
            build_transfer(
                date_requested=a_datetime(year=expected_year, month=expected_month, day=4)
            )
        ],
    )
    reporting_window = MonthlyReportingWindow.prior_to(
        date_anchor=a_datetime(year=expected_year, month=9), number_of_months=1
    )

    actual = construct_practice_summary(
        practice_metrics=practice_transfer_metrics, reporting_window=reporting_window
    )

    assert actual.metrics[0].year == expected_year
    assert actual.metrics[0].month == expected_month


def test_returns_requester_sla_metrics_deprecated():

    transfers = [
        a_transfer_integrated_within_3_days(date_requested=a_datetime(year=2019, month=12))
    ]
    practice_transfer_metrics = PracticeTransferMetrics(ods_code=a_string(), transfers=transfers)

    reporting_window = MonthlyReportingWindow.prior_to(
        date_anchor=a_datetime(year=2020, month=1), number_of_months=1
    )

    expected_requester_sla_metrics = IntegratedPracticeMetricsPresentation(
        transfer_count=1,
        within_3_days_percentage=100,
        within_8_days_percentage=0,
        beyond_8_days_percentage=0,
    )

    actual = construct_practice_summary(
        practice_metrics=practice_transfer_metrics, reporting_window=reporting_window
    )
    time_to_integrate_sla = actual.metrics[0].requester.integrated

    assert time_to_integrate_sla == expected_requester_sla_metrics


def test_returns_requester_sla_metrics_for_two_metric_months_deprecated():

    transfers = [
        a_transfer_integrated_within_3_days(date_requested=a_datetime(year=2019, month=12)),
        a_transfer_integrated_within_3_days(date_requested=a_datetime(year=2019, month=11)),
    ]
    practice_transfer_metrics = PracticeTransferMetrics(ods_code=a_string(), transfers=transfers)

    reporting_window = MonthlyReportingWindow.prior_to(
        date_anchor=a_datetime(year=2020, month=1), number_of_months=2
    )

    expected_requester_sla_metrics = IntegratedPracticeMetricsPresentation(
        transfer_count=1,
        within_3_days_percentage=100,
        within_8_days_percentage=0,
        beyond_8_days_percentage=0,
    )

    actual = construct_practice_summary(
        practice_metrics=practice_transfer_metrics, reporting_window=reporting_window
    )

    actual_december_metrics = actual.metrics[0]
    actual_november_metrics = actual.metrics[1]

    assert actual_november_metrics.requester.integrated == expected_requester_sla_metrics
    assert actual_december_metrics.requester.integrated == expected_requester_sla_metrics
    assert actual_december_metrics.year == 2019
    assert actual_december_metrics.month == 12
    assert actual_november_metrics.year == 2019
    assert actual_november_metrics.month == 11


def test_returns_requester_transfers_received():
    transfers = [
        a_transfer_integrated_within_3_days(date_requested=a_datetime(year=2019, month=12))
    ]
    practice_transfer_metrics = PracticeTransferMetrics(ods_code=a_string(), transfers=transfers)

    reporting_window = MonthlyReportingWindow.prior_to(
        date_anchor=a_datetime(year=2020, month=1), number_of_months=1
    )

    expected_requester_transfers_received = TransfersReceivedPresentation(
        transfer_count=1,
        awaiting_integration=AwaitingIntegration(percentage=0.0),
        integrated=IntegratedPracticeMetricsPresentation(
            transfer_count=1,
            within_3_days_percentage=100.0,
            within_8_days_percentage=0.0,
            beyond_8_days_percentage=0.0,
        ),
    )

    actual = construct_practice_summary(
        practice_metrics=practice_transfer_metrics, reporting_window=reporting_window
    )
    actual_requester_transfers_received = actual.metrics[0].requester.transfers_received

    assert actual_requester_transfers_received == expected_requester_transfers_received


def test_returns_requester_transfers_received_for_two_metric_months():
    transfers = [
        a_transfer_integrated_within_3_days(date_requested=a_datetime(year=2019, month=12)),
        a_transfer_integrated_within_3_days(date_requested=a_datetime(year=2019, month=11)),
    ]
    practice_transfer_metrics = PracticeTransferMetrics(ods_code=a_string(), transfers=transfers)

    reporting_window = MonthlyReportingWindow.prior_to(
        date_anchor=a_datetime(year=2020, month=1), number_of_months=2
    )

    expected_requester_transfers_received = TransfersReceivedPresentation(
        transfer_count=1,
        awaiting_integration=AwaitingIntegration(percentage=0.0),
        integrated=IntegratedPracticeMetricsPresentation(
            transfer_count=1,
            within_3_days_percentage=100.0,
            within_8_days_percentage=0.0,
            beyond_8_days_percentage=0.0,
        ),
    )

    actual = construct_practice_summary(
        practice_metrics=practice_transfer_metrics, reporting_window=reporting_window
    )
    actual_december_metrics = actual.metrics[0]
    actual_november_metrics = actual.metrics[1]

    assert (
        actual_november_metrics.requester.transfers_received
        == expected_requester_transfers_received
    )
    assert (
        actual_december_metrics.requester.transfers_received
        == expected_requester_transfers_received
    )
    assert actual_december_metrics.year == 2019
    assert actual_december_metrics.month == 12
    assert actual_november_metrics.year == 2019
    assert actual_november_metrics.month == 11
