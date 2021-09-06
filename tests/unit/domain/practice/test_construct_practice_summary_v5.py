from prmcalculator.domain.practice.construct_practice_summary_v5 import (
    construct_practice_summary,
    IntegratedPracticeMetricsPresentation,
    TransfersReceivedPresentation,
    AwaitingIntegration,
)

from prmcalculator.domain.practice.practice_transfer_metrics import PracticeTransferMetrics
from prmcalculator.utils.reporting_window import MonthlyReportingWindow
from tests.builders.common import a_datetime, a_date_in, a_string
from tests.builders.gp2gp import (
    build_transfer,
    a_transfer_integrated_within_3_days,
    a_transfer_integrated_between_3_and_8_days,
    a_transfer_integrated_beyond_8_days,
)
from tests.builders.ods_portal import build_practice_details


def test_returns_ods_code_and_name():
    expected_ods_code = "A12345"
    expected_name = "Test GP Practice"
    reporting_window = MonthlyReportingWindow.prior_to(
        date_anchor=a_datetime(year=2021, month=8), number_of_months=1
    )
    practice_details = build_practice_details(name=expected_name, ods_code=expected_ods_code)

    practice_transfer_metrics = PracticeTransferMetrics(
        ods_code=expected_ods_code,
        transfers=[build_transfer(date_requested=a_datetime(year=2021, month=7, day=4))],
    )

    actual = construct_practice_summary(
        practice_details=practice_details,
        practice_metrics=practice_transfer_metrics,
        reporting_window=reporting_window,
    )

    assert actual.ods_code == expected_ods_code
    assert actual.name == expected_name


def test_returns_year_and_month_for_first_metric():
    expected_year = 2019
    expected_month = 8

    practice_details = build_practice_details()

    reporting_window = MonthlyReportingWindow.prior_to(
        date_anchor=a_datetime(year=expected_year, month=9), number_of_months=1
    )
    practice_transfer_metrics = PracticeTransferMetrics(
        ods_code=a_string(),
        transfers=[
            build_transfer(
                date_requested=a_datetime(year=expected_year, month=expected_month, day=4)
            )
        ],
    )

    actual = construct_practice_summary(
        practice_details=practice_details,
        practice_metrics=practice_transfer_metrics,
        reporting_window=reporting_window,
    )

    assert actual.metrics[0].year == expected_year
    assert actual.metrics[0].month == expected_month


def test_returns_requester_transfers_received():
    a_date_in_2019_12 = a_date_in(year=2019, month=12)

    transfers = [
        a_transfer_integrated_within_3_days(date_requested=a_date_in_2019_12()),
        a_transfer_integrated_between_3_and_8_days(date_requested=a_date_in_2019_12()),
        a_transfer_integrated_beyond_8_days(date_requested=a_date_in_2019_12()),
    ]
    reporting_window = MonthlyReportingWindow.prior_to(
        date_anchor=a_datetime(year=2020, month=1), number_of_months=1
    )
    practice_transfer_metrics = PracticeTransferMetrics(ods_code=a_string(), transfers=transfers)

    practice_details = build_practice_details()
    expected_requester_transfers_received = TransfersReceivedPresentation(
        transfer_count=3,
        awaiting_integration=AwaitingIntegration(percentage=0.0),
        integrated=IntegratedPracticeMetricsPresentation(
            within_3_days_percentage=33.3,
            within_8_days_percentage=33.3,
            beyond_8_days_percentage=33.3,
        ),
    )

    actual = construct_practice_summary(
        practice_details=practice_details,
        practice_metrics=practice_transfer_metrics,
        reporting_window=reporting_window,
    )
    actual_requester_transfers_received = actual.metrics[0].requester.transfers_received

    assert actual_requester_transfers_received == expected_requester_transfers_received


def test_returns_requester_transfers_received_for_two_metric_months():
    transfers = [
        a_transfer_integrated_within_3_days(date_requested=a_datetime(year=2019, month=12)),
        a_transfer_integrated_within_3_days(date_requested=a_datetime(year=2019, month=11)),
    ]
    reporting_window = MonthlyReportingWindow.prior_to(
        date_anchor=a_datetime(year=2020, month=1), number_of_months=2
    )
    practice_transfer_metrics = PracticeTransferMetrics(ods_code=a_string(), transfers=transfers)
    practice_details = build_practice_details()
    expected_requester_transfers_received = TransfersReceivedPresentation(
        transfer_count=1,
        awaiting_integration=AwaitingIntegration(percentage=0.0),
        integrated=IntegratedPracticeMetricsPresentation(
            within_3_days_percentage=100.0,
            within_8_days_percentage=0.0,
            beyond_8_days_percentage=0.0,
        ),
    )

    actual = construct_practice_summary(
        practice_details=practice_details,
        practice_metrics=practice_transfer_metrics,
        reporting_window=reporting_window,
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
    assert len(actual.metrics) == 2


def test_returns_default_requester_transfers_received_for_two_metric_months_with_no_transfers():
    reporting_window = MonthlyReportingWindow.prior_to(
        date_anchor=a_datetime(year=2021, month=8), number_of_months=2
    )
    practice_transfer_metrics = PracticeTransferMetrics(ods_code=a_string(), transfers=[])
    practice_details = build_practice_details()

    actual = construct_practice_summary(
        practice_details=practice_details,
        practice_metrics=practice_transfer_metrics,
        reporting_window=reporting_window,
    )

    expected_transfers_received = TransfersReceivedPresentation(
        transfer_count=0,
        awaiting_integration=AwaitingIntegration(percentage=None),
        integrated=IntegratedPracticeMetricsPresentation(
            within_3_days_percentage=None,
            within_8_days_percentage=None,
            beyond_8_days_percentage=None,
        ),
    )

    for month_metrics in actual.metrics:
        actual_transfers_received = month_metrics.requester.transfers_received
        assert actual_transfers_received == expected_transfers_received
