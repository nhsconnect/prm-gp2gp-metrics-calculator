from collections import Counter
from datetime import timedelta
from typing import Set, Iterator, List

import pytest

from prmcalculator.domain.practice.practice_lookup import PracticeLookup
from prmcalculator.domain.gp2gp.transfer import Transfer, Practice
from prmcalculator.domain.ods_portal.organisation_metadata import PracticeDetails
from prmcalculator.domain.practice.deprecated.metrics_calculator_deprecated import (
    PracticeMetricsDeprecated,
    calculate_monthly_sla_by_practice_deprecated,
    IntegratedPracticeMetricsDeprecated,
    MonthlyMetricsDeprecated,
)
from prmcalculator.utils.reporting_window import MonthlyReportingWindow

from tests.builders.common import a_string, a_datetime
from tests.builders.gp2gp import build_transfer

reporting_window = MonthlyReportingWindow.prior_to(
    date_anchor=a_datetime(year=2020, month=1), number_of_months=1
)


def _assert_has_ods_codes(practices: Iterator[PracticeMetricsDeprecated], expected: Set[str]):
    actual_counts = Counter((practice.ods_code for practice in practices))
    expected_counts = Counter(expected)
    assert actual_counts == expected_counts


def _assert_summaries_have_integrated_practice_metrics(
    practices: Iterator[PracticeMetricsDeprecated],
    expected_slas: List[IntegratedPracticeMetricsDeprecated],
):
    practice_list = list(practices)

    actual_slas = [
        monthly_metrics.integrated
        for practice in practice_list
        for monthly_metrics in practice.metrics
    ]

    assert actual_slas == expected_slas


def test_groups_by_ods_code_given_single_practice_and_single_transfer():
    lookup = PracticeLookup(
        [PracticeDetails(asids=["121212121212"], ods_code="A12345", name=a_string())]
    )
    transfers = [
        build_transfer(requesting_practice=Practice(asid="121212121212", supplier=a_string(12)))
    ]

    actual = calculate_monthly_sla_by_practice_deprecated(lookup, transfers, reporting_window)

    _assert_has_ods_codes(actual, {"A12345"})


def test_groups_by_ods_code_given_single_practice_and_no_transfers():
    lookup = PracticeLookup(
        [PracticeDetails(asids=["121212121212"], ods_code="A12345", name=a_string())]
    )
    transfers: List[Transfer] = []

    actual = calculate_monthly_sla_by_practice_deprecated(lookup, transfers, reporting_window)

    _assert_has_ods_codes(actual, {"A12345"})


def test_warns_about_transfer_with_unexpected_asid():
    lookup = PracticeLookup([])
    transfers = [
        build_transfer(requesting_practice=Practice(asid="121212121212", supplier=a_string(12)))
    ]

    with pytest.warns(RuntimeWarning):
        calculate_monthly_sla_by_practice_deprecated(lookup, transfers, reporting_window)


def test_groups_by_asid_given_two_practices_and_two_transfers_from_different_practices():
    lookup = PracticeLookup(
        [
            PracticeDetails(asids=["121212121212"], ods_code="A12345", name=a_string()),
            PracticeDetails(asids=["343434343434"], ods_code="X67890", name=a_string()),
        ]
    )
    transfers = [
        build_transfer(requesting_practice=Practice(asid="121212121212", supplier=a_string(12))),
        build_transfer(requesting_practice=Practice(asid="343434343434", supplier=a_string(12))),
    ]

    actual = calculate_monthly_sla_by_practice_deprecated(lookup, transfers, reporting_window)

    _assert_has_ods_codes(actual, {"A12345", "X67890"})


def test_groups_by_asid_given_single_practice_and_transfers_from_the_same_practice():
    lookup = PracticeLookup(
        [PracticeDetails(asids=["121212121212"], ods_code="A12345", name=a_string())]
    )
    transfers = [
        build_transfer(requesting_practice=Practice(asid="121212121212", supplier=a_string(12))),
        build_transfer(requesting_practice=Practice(asid="121212121212", supplier=a_string(12))),
    ]

    actual = calculate_monthly_sla_by_practice_deprecated(lookup, transfers, reporting_window)

    _assert_has_ods_codes(actual, {"A12345"})


def test_contains_practice_name():
    expected_name = "A Practice"
    lookup = PracticeLookup(
        [PracticeDetails(asids=[a_string()], ods_code=a_string(), name=expected_name)]
    )
    transfers: List[Transfer] = []

    actual_name = list(
        calculate_monthly_sla_by_practice_deprecated(lookup, transfers, reporting_window)
    )[0].name

    assert actual_name == expected_name


def test_returns_practice_sla_metrics_placeholder_given_a_list_with_one_practice_and_no_metrics():
    lookup = PracticeLookup(
        [PracticeDetails(asids=["121212121212"], ods_code="A12345", name=a_string())]
    )
    transfers: List[Transfer] = []

    actual = calculate_monthly_sla_by_practice_deprecated(lookup, transfers, reporting_window)
    expected = [
        IntegratedPracticeMetricsDeprecated(
            transfer_count=0, within_3_days=0, within_8_days=0, beyond_8_days=0
        )
    ]

    _assert_summaries_have_integrated_practice_metrics(actual, expected)


def test_calculate_sla_by_practice_calculates_sla_given_one_transfer_within_3_days():
    lookup = PracticeLookup(
        [PracticeDetails(asids=["121212121212"], ods_code="A12345", name=a_string())]
    )
    transfer = build_transfer(
        requesting_practice=Practice(asid="121212121212", supplier=a_string(12)),
        sla_duration=timedelta(hours=1, minutes=10),
    )

    actual = calculate_monthly_sla_by_practice_deprecated(lookup, [transfer], reporting_window)
    expected = [
        IntegratedPracticeMetricsDeprecated(
            transfer_count=1, within_3_days=1, within_8_days=0, beyond_8_days=0
        )
    ]

    _assert_summaries_have_integrated_practice_metrics(actual, expected)


def test_calculate_sla_by_practice_calculates_sla_given_one_transfer_within_8_days():
    lookup = PracticeLookup(
        [PracticeDetails(asids=["121212121212"], ods_code="A12345", name=a_string())]
    )
    transfer = build_transfer(
        requesting_practice=Practice(asid="121212121212", supplier=a_string(12)),
        sla_duration=timedelta(days=7, hours=1, minutes=10),
    )
    actual = calculate_monthly_sla_by_practice_deprecated(lookup, [transfer], reporting_window)
    expected = [
        IntegratedPracticeMetricsDeprecated(
            transfer_count=1, within_3_days=0, within_8_days=1, beyond_8_days=0
        )
    ]

    _assert_summaries_have_integrated_practice_metrics(actual, expected)


def test_calculate_sla_by_practice_calculates_sla_given_one_transfer_beyond_8_days():
    lookup = PracticeLookup(
        [PracticeDetails(asids=["121212121212"], ods_code="A12345", name=a_string())]
    )
    transfer = build_transfer(
        requesting_practice=Practice(asid="121212121212", supplier=a_string(12)),
        sla_duration=timedelta(days=8, hours=1, minutes=10),
    )
    actual = calculate_monthly_sla_by_practice_deprecated(lookup, [transfer], reporting_window)
    expected = [
        IntegratedPracticeMetricsDeprecated(
            transfer_count=1, within_3_days=0, within_8_days=0, beyond_8_days=1
        )
    ]

    _assert_summaries_have_integrated_practice_metrics(actual, expected)


def test_counts_second_asid_for_practice_with_two_asids():
    lookup = PracticeLookup(
        [
            PracticeDetails(
                asids=["121212121212", "343434343434"], ods_code="A12345", name=a_string()
            )
        ]
    )
    transfer = build_transfer(
        requesting_practice=Practice(asid="343434343434", supplier=a_string(12)),
        sla_duration=timedelta(hours=1, minutes=10),
    )

    actual = calculate_monthly_sla_by_practice_deprecated(lookup, [transfer], reporting_window)
    expected = [
        IntegratedPracticeMetricsDeprecated(
            transfer_count=1, within_3_days=1, within_8_days=0, beyond_8_days=0
        )
    ]

    _assert_summaries_have_integrated_practice_metrics(actual, expected)


def test_counts_both_asids_for_practice_with_two_asids():
    lookup = PracticeLookup(
        [
            PracticeDetails(
                asids=["121212121212", "343434343434"], ods_code="A12345", name=a_string()
            )
        ]
    )
    transfers = [
        build_transfer(
            requesting_practice=Practice(asid="343434343434", supplier=a_string(12)),
            sla_duration=timedelta(hours=1, minutes=10),
        ),
        build_transfer(
            requesting_practice=Practice(asid="121212121212", supplier=a_string(12)),
            sla_duration=timedelta(days=5, hours=1, minutes=10),
        ),
    ]

    actual = calculate_monthly_sla_by_practice_deprecated(lookup, transfers, reporting_window)
    expected = [
        IntegratedPracticeMetricsDeprecated(
            transfer_count=2, within_3_days=1, within_8_days=1, beyond_8_days=0
        )
    ]

    _assert_summaries_have_integrated_practice_metrics(actual, expected)


def test_calculates_sla_given_two_transfers_from_different_months():
    two_month_reporting_window = MonthlyReportingWindow.prior_to(
        date_anchor=a_datetime(year=2021, month=2), number_of_months=2
    )

    lookup = PracticeLookup(
        [PracticeDetails(asids=["121212121212"], ods_code="A12345", name=a_string())]
    )
    transfers = [
        build_transfer(
            requesting_practice=Practice(asid="121212121212", supplier=a_string(12)),
            sla_duration=timedelta(days=10),
            date_requested=a_datetime(year=2020, month=12),
        ),
        build_transfer(
            requesting_practice=Practice(asid="121212121212", supplier=a_string(12)),
            sla_duration=timedelta(hours=1, minutes=10),
            date_requested=a_datetime(year=2021, month=1),
        ),
    ]

    actual = calculate_monthly_sla_by_practice_deprecated(
        lookup, transfers, two_month_reporting_window
    )
    expected = [
        IntegratedPracticeMetricsDeprecated(
            transfer_count=1, within_3_days=1, within_8_days=0, beyond_8_days=0
        ),
        IntegratedPracticeMetricsDeprecated(
            transfer_count=1, within_3_days=0, within_8_days=0, beyond_8_days=1
        ),
    ]

    _assert_summaries_have_integrated_practice_metrics(actual, expected)


def test_calculate_sla_by_practice_calculates_sla_given_transfers_for_2_practices():
    lookup = PracticeLookup(
        [
            PracticeDetails(asids=["121212121212"], ods_code="A12345", name="A Practice"),
            PracticeDetails(asids=["343434343434"], ods_code="B12345", name="Another Practice"),
        ]
    )
    transfers = [
        build_transfer(
            requesting_practice=Practice(asid="121212121212", supplier=a_string(12)),
            sla_duration=timedelta(days=8, hours=1, minutes=10),
        ),
        build_transfer(
            requesting_practice=Practice(asid="343434343434", supplier=a_string(12)),
            sla_duration=timedelta(days=4, hours=1, minutes=10),
        ),
        build_transfer(
            requesting_practice=Practice(asid="121212121212", supplier=a_string(12)),
            sla_duration=timedelta(days=0, hours=1, minutes=10),
        ),
        build_transfer(
            requesting_practice=Practice(asid="343434343434", supplier=a_string(12)),
            sla_duration=timedelta(days=8, hours=1, minutes=10),
        ),
        build_transfer(
            requesting_practice=Practice(asid="343434343434", supplier=a_string(12)),
            sla_duration=timedelta(days=5, hours=1, minutes=10),
        ),
    ]

    expected = [
        PracticeMetricsDeprecated(
            ods_code="A12345",
            name="A Practice",
            metrics=[
                MonthlyMetricsDeprecated(
                    year=2019,
                    month=12,
                    integrated=IntegratedPracticeMetricsDeprecated(
                        transfer_count=2, within_3_days=1, within_8_days=0, beyond_8_days=1
                    ),
                )
            ],
        ),
        PracticeMetricsDeprecated(
            ods_code="B12345",
            name="Another Practice",
            metrics=[
                MonthlyMetricsDeprecated(
                    year=2019,
                    month=12,
                    integrated=IntegratedPracticeMetricsDeprecated(
                        transfer_count=3, within_3_days=0, within_8_days=2, beyond_8_days=1
                    ),
                ),
            ],
        ),
    ]

    actual = calculate_monthly_sla_by_practice_deprecated(lookup, transfers, reporting_window)

    assert list(actual) == expected
