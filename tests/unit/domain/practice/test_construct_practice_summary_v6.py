from prmcalculator.domain.practice.construct_practice_summary_v6 import (
    construct_practice_summary,
)

from prmcalculator.domain.practice.practice_transfer_metrics import PracticeTransferMetrics
from prmcalculator.utils.reporting_window import MonthlyReportingWindow
from tests.builders.common import a_datetime, a_date_in, a_string
from tests.builders.gp2gp import (
    build_transfer,
    a_transfer_integrated_within_3_days,
    a_transfer_integrated_beyond_8_days,
    a_transfer_with_a_final_error,
    a_transfer_that_was_never_integrated,
    a_transfer_integrated_between_3_and_8_days,
)


def test_returns_ods_code_and_name():
    expected_ods_code = "A12345"
    expected_name = "Test GP Practice"
    reporting_window = MonthlyReportingWindow.prior_to(
        date_anchor=a_datetime(year=2021, month=8), number_of_months=1
    )

    practice_transfer_metrics = PracticeTransferMetrics(
        ods_code=expected_ods_code,
        name=expected_name,
        transfers=[build_transfer(date_requested=a_datetime(year=2021, month=7, day=4))],
    )

    actual = construct_practice_summary(
        practice_metrics=practice_transfer_metrics,
        reporting_window=reporting_window,
    )

    assert actual.ods_code == expected_ods_code
    assert actual.name == expected_name


def test_returns_year_and_month_for_first_metric():
    expected_year = 2019
    expected_month = 8

    reporting_window = MonthlyReportingWindow.prior_to(
        date_anchor=a_datetime(year=expected_year, month=9), number_of_months=1
    )
    practice_transfer_metrics = PracticeTransferMetrics(
        ods_code=a_string(),
        name=a_string(),
        transfers=[
            build_transfer(
                date_requested=a_datetime(year=expected_year, month=expected_month, day=4)
            )
        ],
    )

    actual = construct_practice_summary(
        practice_metrics=practice_transfer_metrics,
        reporting_window=reporting_window,
    )

    assert actual.metrics[0].year == expected_year
    assert actual.metrics[0].month == expected_month


def test_returns_requester_transfers_requested_count():
    a_date_in_2019_12 = a_date_in(year=2019, month=12)

    transfers = [
        a_transfer_integrated_within_3_days(date_requested=a_date_in_2019_12()),
        a_transfer_integrated_beyond_8_days(date_requested=a_date_in_2019_12()),
        a_transfer_that_was_never_integrated(date_requested=a_date_in_2019_12()),
        a_transfer_with_a_final_error(date_requested=a_date_in_2019_12()),
    ]
    reporting_window = MonthlyReportingWindow.prior_to(
        date_anchor=a_datetime(year=2020, month=1), number_of_months=1
    )
    practice_transfer_metrics = PracticeTransferMetrics(
        ods_code=a_string(), name=a_string(), transfers=transfers
    )

    expected_requested_count = 4
    actual = construct_practice_summary(
        practice_metrics=practice_transfer_metrics,
        reporting_window=reporting_window,
    )
    actual_requested_count = actual.metrics[0].requested_transfers.requested_count

    assert actual_requested_count == expected_requested_count


def test_returns_requester_transfers_received_count():
    a_date_in_2019_12 = a_date_in(year=2019, month=12)

    transfers = [
        a_transfer_integrated_within_3_days(date_requested=a_date_in_2019_12()),
        a_transfer_integrated_between_3_and_8_days(date_requested=a_date_in_2019_12()),
        a_transfer_integrated_beyond_8_days(date_requested=a_date_in_2019_12()),
        a_transfer_that_was_never_integrated(date_requested=a_date_in_2019_12()),
    ]
    reporting_window = MonthlyReportingWindow.prior_to(
        date_anchor=a_datetime(year=2020, month=1), number_of_months=1
    )

    practice_transfer_metrics = PracticeTransferMetrics(
        ods_code=a_string(), name=a_string(), transfers=transfers
    )

    expected_received_count = 4

    actual = construct_practice_summary(
        practice_metrics=practice_transfer_metrics,
        reporting_window=reporting_window,
    )
    actual_received_count = actual.metrics[0].requested_transfers.received_count

    assert actual_received_count == expected_received_count


def test_returns_requester_transfers_integrated_count():
    a_date_in_2019_12 = a_date_in(year=2019, month=12)

    transfers = [
        a_transfer_integrated_within_3_days(date_requested=a_date_in_2019_12()),
        a_transfer_integrated_between_3_and_8_days(date_requested=a_date_in_2019_12()),
        a_transfer_integrated_beyond_8_days(date_requested=a_date_in_2019_12()),
    ]
    reporting_window = MonthlyReportingWindow.prior_to(
        date_anchor=a_datetime(year=2020, month=1), number_of_months=1
    )

    practice_transfer_metrics = PracticeTransferMetrics(
        ods_code=a_string(), name=a_string(), transfers=transfers
    )

    expected_integrated_count = 3

    actual = construct_practice_summary(
        practice_metrics=practice_transfer_metrics,
        reporting_window=reporting_window,
    )
    actual_integrated_count = actual.metrics[0].requested_transfers.integrated_count

    assert actual_integrated_count == expected_integrated_count


def test_returns_requester_transfers_integrated_within_3_days_count():
    a_date_in_2019_12 = a_date_in(year=2019, month=12)

    transfers = [
        a_transfer_integrated_within_3_days(date_requested=a_date_in_2019_12()),
        a_transfer_integrated_within_3_days(date_requested=a_date_in_2019_12()),
        a_transfer_integrated_between_3_and_8_days(date_requested=a_date_in_2019_12()),
    ]
    reporting_window = MonthlyReportingWindow.prior_to(
        date_anchor=a_datetime(year=2020, month=1), number_of_months=1
    )

    practice_transfer_metrics = PracticeTransferMetrics(
        ods_code=a_string(), name=a_string(), transfers=transfers
    )

    expected_integrated_within_3_days_count = 2

    actual = construct_practice_summary(
        practice_metrics=practice_transfer_metrics,
        reporting_window=reporting_window,
    )
    actual_integrated_within_3_days_count = actual.metrics[
        0
    ].requested_transfers.integrated_within_3_days_count

    assert actual_integrated_within_3_days_count == expected_integrated_within_3_days_count


def test_returns_requester_transfers_integrated_within_8_days_count():
    a_date_in_2019_12 = a_date_in(year=2019, month=12)

    transfers = [
        a_transfer_integrated_within_3_days(date_requested=a_date_in_2019_12()),
        a_transfer_integrated_between_3_and_8_days(date_requested=a_date_in_2019_12()),
        a_transfer_integrated_between_3_and_8_days(date_requested=a_date_in_2019_12()),
    ]
    reporting_window = MonthlyReportingWindow.prior_to(
        date_anchor=a_datetime(year=2020, month=1), number_of_months=1
    )

    practice_transfer_metrics = PracticeTransferMetrics(
        ods_code=a_string(), name=a_string(), transfers=transfers
    )

    expected_integrated_within_8_days_count = 2

    actual = construct_practice_summary(
        practice_metrics=practice_transfer_metrics,
        reporting_window=reporting_window,
    )
    actual_integrated_within_8_days_count = actual.metrics[
        0
    ].requested_transfers.integrated_within_8_days_count

    assert actual_integrated_within_8_days_count == expected_integrated_within_8_days_count


def test_returns_requester_transfers_integrated_beyond_8_days_count():
    a_date_in_2019_12 = a_date_in(year=2019, month=12)

    transfers = [
        a_transfer_integrated_between_3_and_8_days(date_requested=a_date_in_2019_12()),
        a_transfer_integrated_beyond_8_days(date_requested=a_date_in_2019_12()),
        a_transfer_integrated_beyond_8_days(date_requested=a_date_in_2019_12()),
    ]
    reporting_window = MonthlyReportingWindow.prior_to(
        date_anchor=a_datetime(year=2020, month=1), number_of_months=1
    )

    practice_transfer_metrics = PracticeTransferMetrics(
        ods_code=a_string(), name=a_string(), transfers=transfers
    )

    expected_integrated_beyond_8_days_count = 2

    actual = construct_practice_summary(
        practice_metrics=practice_transfer_metrics,
        reporting_window=reporting_window,
    )
    actual_integrated_beyond_8_days_count = actual.metrics[
        0
    ].requested_transfers.integrated_beyond_8_days_count

    assert actual_integrated_beyond_8_days_count == expected_integrated_beyond_8_days_count


def test_returns_requester_transfers_awaiting_integration_count():
    a_date_in_2019_12 = a_date_in(year=2019, month=12)

    transfers = [
        a_transfer_integrated_beyond_8_days(date_requested=a_date_in_2019_12()),
        a_transfer_that_was_never_integrated(date_requested=a_date_in_2019_12()),
        a_transfer_that_was_never_integrated(date_requested=a_date_in_2019_12()),
    ]
    reporting_window = MonthlyReportingWindow.prior_to(
        date_anchor=a_datetime(year=2020, month=1), number_of_months=1
    )

    practice_transfer_metrics = PracticeTransferMetrics(
        ods_code=a_string(), name=a_string(), transfers=transfers
    )

    expected_awaiting_integration_count = 2

    actual = construct_practice_summary(
        practice_metrics=practice_transfer_metrics,
        reporting_window=reporting_window,
    )
    actual_awaiting_integration_count = actual.metrics[
        0
    ].requested_transfers.awaiting_integration_count

    assert actual_awaiting_integration_count == expected_awaiting_integration_count
