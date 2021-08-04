import pytest

from prmcalculator.utils.reporting_window import MonthlyReportingWindow
from tests.builders.common import a_datetime

default_number_of_months = 1


def test_prior_to_correctly_determines_metric_month():
    moment = a_datetime(year=2021, month=3, day=4)

    reporting_window = MonthlyReportingWindow.prior_to(moment, default_number_of_months)

    expected = 2

    actual = reporting_window.metric_month

    assert actual == expected


def test_prior_to_correctly_determines_metric_year():
    moment = a_datetime(year=2021, month=3, day=4)

    reporting_window = MonthlyReportingWindow.prior_to(moment, default_number_of_months)

    expected = 2021

    actual = reporting_window.metric_year

    assert actual == expected


def test_prior_to_correctly_determines_metric_month_over_new_year():
    moment = a_datetime(year=2021, month=1, day=4)

    reporting_window = MonthlyReportingWindow.prior_to(moment, default_number_of_months)

    expected = 12

    actual = reporting_window.metric_month

    assert actual == expected


def test_prior_to_correctly_determines_metric_year_over_new_year():
    moment = a_datetime(year=2021, month=1, day=4)

    reporting_window = MonthlyReportingWindow.prior_to(moment, default_number_of_months)

    expected = 2020

    actual = reporting_window.metric_year

    assert actual == expected


def test_prior_to_correctly_determines_overflow_month():
    moment = a_datetime(year=2021, month=3, day=4)

    reporting_window = MonthlyReportingWindow.prior_to(moment, default_number_of_months)

    expected = 3

    actual = reporting_window.overflow_month

    assert actual == expected


def test_prior_to_correctly_determines_overflow_year():
    moment = a_datetime(year=2021, month=3, day=4)

    reporting_window = MonthlyReportingWindow.prior_to(moment, default_number_of_months)

    expected = 2021

    actual = reporting_window.overflow_year

    assert actual == expected


def test_prior_to_correctly_determines_multiple_metric_months():
    moment = a_datetime(year=2021, month=2, day=4)

    reporting_window = MonthlyReportingWindow.prior_to(date_anchor=moment, number_of_months=3)

    expected = [(2021, 1), (2020, 12), (2020, 11)]

    actual = reporting_window.metric_months

    assert actual == expected


@pytest.mark.parametrize(
    "test_case",
    [
        ({"date": a_datetime(year=2021, month=1, day=31), "expected": False}),
        ({"date": a_datetime(year=2021, month=2, day=1), "expected": True}),
        ({"date": a_datetime(year=2021, month=2, day=20), "expected": True}),
        ({"date": a_datetime(year=2021, month=2, day=28), "expected": True}),
        ({"date": a_datetime(year=2021, month=3, day=1), "expected": False}),
    ],
)
def test_contains_returns_correct_boolean(test_case):
    moment = a_datetime(year=2021, month=3, day=4)

    reporting_window = MonthlyReportingWindow.prior_to(moment, default_number_of_months)

    actual = reporting_window.contains(test_case["date"])

    assert actual == test_case["expected"]
