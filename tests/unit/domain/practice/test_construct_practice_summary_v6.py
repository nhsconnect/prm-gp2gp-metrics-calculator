from prmcalculator.domain.practice.construct_practice_summary_v6 import construct_practice_summary

from prmcalculator.domain.practice.practice_transfer_metrics import PracticeTransferMetrics
from prmcalculator.utils.reporting_window import MonthlyReportingWindow
from tests.builders.common import a_datetime
from tests.builders.gp2gp import build_transfer
from tests.builders.ods_portal import build_practice_details


def test_returns_ods_code_and_name():
    expected_ods_code = "A12345"
    expected_name = "Test GP Practice"
    reporting_window = MonthlyReportingWindow.prior_to(
        date_anchor=a_datetime(year=2021, month=8), number_of_months=1
    )
    practice_details = build_practice_details(name=expected_name, ods_code=expected_ods_code)

    practice_transfer_metrics = PracticeTransferMetrics(
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
