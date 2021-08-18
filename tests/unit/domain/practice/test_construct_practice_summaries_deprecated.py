from collections import Counter
from typing import Set, Iterable

from prmcalculator.domain.practice.deprecated.metrics_calculator_deprecated import (
    MonthlyMetricsDeprecated,
    IntegratedPracticeMetricsDeprecated,
)
from prmcalculator.domain.practice.deprecated.metrics_presentation_deprecated import (
    construct_practice_summaries_deprecated,
    IntegratedPracticeMetricsPresentationDeprecated,
    RequesterMetricsDeprecated,
    MonthlyMetricsPresentationDeprecated,
    PracticeSummaryDeprecated,
)
from tests.builders.gp2gp import build_practice_metrics


def _assert_has_ods_codes(practices: Iterable[PracticeSummaryDeprecated], expected: Set[str]):
    actual_counts = Counter((practice.ods_code for practice in practices))
    expected_counts = Counter(expected)
    assert actual_counts == expected_counts


def test_has_correct_ods_code_given_a_single_practice():
    sla_metrics = [build_practice_metrics(ods_code="A12345")]

    expected_ods_codes = "A12345"

    actual = construct_practice_summaries_deprecated(sla_metrics)

    assert actual[0].ods_code == expected_ods_codes


def test_has_correct_ods_code_given_two_practices():
    sla_metrics = [
        build_practice_metrics(ods_code="A12345"),
        build_practice_metrics(ods_code="Z56789"),
    ]

    expected_ods_codes = {"A12345", "Z56789"}

    actual = construct_practice_summaries_deprecated(sla_metrics)

    _assert_has_ods_codes(actual, expected_ods_codes)


def test_has_correct_practice_name_given_a_single_practice():
    sla_metrics = [build_practice_metrics(name="A Practice")]

    expected_name = "A Practice"

    actual = construct_practice_summaries_deprecated(sla_metrics)

    assert actual[0].name == expected_name


def test_has_correct_year_given_a_single_practice():
    sla_metrics = [build_practice_metrics(ods_code="A12345")]

    expected_year = 2019

    actual = construct_practice_summaries_deprecated(sla_metrics)

    assert actual[0].metrics[0].year == expected_year


def test_has_correct_month_given_a_single_practice():
    sla_metrics = [build_practice_metrics(ods_code="A12345")]

    expected_month = 12

    actual = construct_practice_summaries_deprecated(sla_metrics)

    assert actual[0].metrics[0].month == expected_month


def test_has_correct_requester_sla_metrics_given_single_practice():
    sla_metrics = [
        build_practice_metrics(transfer_count=3, within_3_days=1, within_8_days=0, beyond_8_days=2)
    ]

    expected_requester_sla_metrics = IntegratedPracticeMetricsPresentationDeprecated(
        transfer_count=3,
        within_3_days_percentage=33.3,
        within_8_days_percentage=0,
        beyond_8_days_percentage=66.7,
    )

    actual = construct_practice_summaries_deprecated(sla_metrics)
    time_to_integrate_sla = actual[0].metrics[0].requester.integrated

    assert time_to_integrate_sla == expected_requester_sla_metrics


def test_has_correct_requester_sla_metrics_given_two_practices():
    sla_metrics = [
        build_practice_metrics(
            ods_code="A12345",
            name="A practice",
            transfer_count=3,
            within_3_days=1,
            within_8_days=0,
            beyond_8_days=2,
        ),
        build_practice_metrics(
            ods_code="Z98765",
            name="Another practice",
            transfer_count=7,
            within_3_days=0,
            within_8_days=5,
            beyond_8_days=2,
        ),
    ]

    expected = [
        PracticeSummaryDeprecated(
            ods_code="A12345",
            name="A practice",
            metrics=[
                MonthlyMetricsPresentationDeprecated(
                    year=2019,
                    month=12,
                    requester=RequesterMetricsDeprecated(
                        integrated=IntegratedPracticeMetricsPresentationDeprecated(
                            transfer_count=3,
                            within_3_days_percentage=33.3,
                            within_8_days_percentage=0.0,
                            beyond_8_days_percentage=66.7,
                        ),
                    ),
                )
            ],
        ),
        PracticeSummaryDeprecated(
            ods_code="Z98765",
            name="Another practice",
            metrics=[
                MonthlyMetricsPresentationDeprecated(
                    year=2019,
                    month=12,
                    requester=RequesterMetricsDeprecated(
                        integrated=IntegratedPracticeMetricsPresentationDeprecated(
                            transfer_count=7,
                            within_3_days_percentage=0.0,
                            within_8_days_percentage=71.4,
                            beyond_8_days_percentage=28.6,
                        ),
                    ),
                )
            ],
        ),
    ]

    actual = construct_practice_summaries_deprecated(sla_metrics)

    assert actual == expected


def test_has_correct_requester_sla_metrics_given_two_metric_months():
    sla_metrics = [
        build_practice_metrics(
            ods_code="A12345",
            name="A practice",
            metrics=[
                MonthlyMetricsDeprecated(
                    year=2020,
                    month=1,
                    integrated=IntegratedPracticeMetricsDeprecated(
                        transfer_count=3,
                        within_3_days=1,
                        within_8_days=0,
                        beyond_8_days=2,
                    ),
                ),
                MonthlyMetricsDeprecated(
                    year=2019,
                    month=12,
                    integrated=IntegratedPracticeMetricsDeprecated(
                        transfer_count=1,
                        within_3_days=0,
                        within_8_days=1,
                        beyond_8_days=0,
                    ),
                ),
            ],
        )
    ]

    expected = [
        PracticeSummaryDeprecated(
            ods_code="A12345",
            name="A practice",
            metrics=[
                MonthlyMetricsPresentationDeprecated(
                    year=2020,
                    month=1,
                    requester=RequesterMetricsDeprecated(
                        integrated=IntegratedPracticeMetricsPresentationDeprecated(
                            transfer_count=3,
                            within_3_days_percentage=33.3,
                            within_8_days_percentage=0,
                            beyond_8_days_percentage=66.7,
                        ),
                    ),
                ),
                MonthlyMetricsPresentationDeprecated(
                    year=2019,
                    month=12,
                    requester=RequesterMetricsDeprecated(
                        integrated=IntegratedPracticeMetricsPresentationDeprecated(
                            transfer_count=1,
                            within_3_days_percentage=0,
                            within_8_days_percentage=100,
                            beyond_8_days_percentage=0,
                        ),
                    ),
                ),
            ],
        ),
    ]

    actual = construct_practice_summaries_deprecated(sla_metrics)

    assert actual == expected
