from datetime import datetime
from typing import List

from prmcalculator.domain.gp2gp.transfer import filter_transfers_by_date_requested, Transfer
from prmcalculator.utils.reporting_window import MonthlyReportingWindow
from tests.builders.gp2gp import build_transfer


def test_includes_transfer_in_a_metric_month():
    metric_month_start = datetime(year=2021, month=2, day=1)

    reporting_window = MonthlyReportingWindow(
        metric_month_start=metric_month_start,
        overflow_month_start=datetime(year=2021, month=3, day=1),
        metric_months=[metric_month_start],
    )

    transfers = [build_transfer(date_requested=datetime(year=2021, month=2, day=15))]

    actual = filter_transfers_by_date_requested(transfers, reporting_window)

    expected = transfers

    assert list(actual) == expected


def test_does_not_include_transfer_before_metric_month():
    metric_month_start = datetime(year=2021, month=2, day=1)

    reporting_window = MonthlyReportingWindow(
        metric_month_start=metric_month_start,
        overflow_month_start=datetime(year=2021, month=3, day=1),
        metric_months=[metric_month_start],
    )

    transfers = [build_transfer(date_requested=datetime(year=2021, month=1, day=4))]

    actual = filter_transfers_by_date_requested(transfers, reporting_window)

    expected: List[Transfer] = []

    assert list(actual) == expected


def test_does_not_include_transfer_after_metric_month():
    metric_month_start = datetime(year=2021, month=2, day=1)

    reporting_window = MonthlyReportingWindow(
        metric_month_start=metric_month_start,
        overflow_month_start=datetime(year=2021, month=3, day=1),
        metric_months=[metric_month_start],
    )

    transfers = [build_transfer(date_requested=datetime(year=2021, month=3, day=4))]

    actual = filter_transfers_by_date_requested(transfers, reporting_window)

    expected: List[Transfer] = []

    assert list(actual) == expected


def test_includes_transfer_on_a_metric_month_start():
    metric_month_start = datetime(year=2021, month=2, day=1)

    reporting_window = MonthlyReportingWindow(
        metric_month_start=metric_month_start,
        overflow_month_start=datetime(year=2021, month=3, day=1),
        metric_months=[metric_month_start],
    )

    transfers = [build_transfer(date_requested=datetime(year=2021, month=2, day=1))]

    actual = filter_transfers_by_date_requested(transfers, reporting_window)

    expected = transfers

    assert list(actual) == expected


def test_includes_transfer_on_a_metric_month_end():
    metric_month_start = datetime(year=2021, month=3, day=1)

    reporting_window = MonthlyReportingWindow(
        metric_month_start=metric_month_start,
        overflow_month_start=datetime(year=2021, month=4, day=1),
        metric_months=[metric_month_start],
    )

    transfers = [build_transfer(date_requested=datetime(year=2021, month=3, day=31))]

    actual = filter_transfers_by_date_requested(transfers, reporting_window)

    expected = transfers

    assert list(actual) == expected


def test_filters_multiple_transfers():
    metric_month_start = datetime(year=2021, month=1, day=1)

    reporting_window = MonthlyReportingWindow(
        metric_month_start=metric_month_start,
        overflow_month_start=datetime(year=2021, month=2, day=1),
        metric_months=[metric_month_start],
    )

    transfer_in_a_metric_month = build_transfer(date_requested=datetime(year=2021, month=1, day=28))
    transfer_before_metric_month = build_transfer(
        date_requested=datetime(year=2020, month=12, day=31)
    )
    transfer_after_metric_month = build_transfer(date_requested=datetime(year=2021, month=2, day=1))

    transfers = [
        transfer_in_a_metric_month,
        transfer_before_metric_month,
        transfer_after_metric_month,
    ]

    actual = filter_transfers_by_date_requested(transfers, reporting_window)

    expected = [transfer_in_a_metric_month]

    assert list(actual) == expected
