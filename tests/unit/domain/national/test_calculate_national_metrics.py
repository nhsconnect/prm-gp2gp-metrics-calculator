from typing import List

import pytest

from prmcalculator.domain.national.metrics_calculator import calculate_national_metrics
from prmcalculator.domain.gp2gp.transfer import Transfer

from tests.builders.gp2gp import (
    an_integrated_transfer,
    a_transfer_with_a_final_error,
    a_transfer_that_was_never_integrated,
    a_transfer_where_the_request_was_never_acknowledged,
    a_transfer_where_no_core_ehr_was_sent,
    a_transfer_where_no_copc_continue_was_sent,
    a_transfer_where_copc_fragments_were_required_but_not_sent,
    a_transfer_where_copc_fragments_remained_unacknowledged,
    a_transfer_where_the_sender_reported_an_unrecoverable_error,
    a_transfer_where_a_copc_triggered_an_error,
    a_transfer_integrated_beyond_8_days,
    a_transfer_integrated_within_3_days,
    a_transfer_integrated_between_3_and_8_days,
)


def test_returns_initiated_transfer_count_default_given_no_transfers():
    national_metrics = calculate_national_metrics([])
    assert national_metrics.initiated_transfer_count == 0


def test_returns_initiated_transfer_count():
    transfers = [
        a_transfer_where_the_request_was_never_acknowledged(),
        an_integrated_transfer(),
    ]
    national_metrics = calculate_national_metrics(transfers)
    assert national_metrics.initiated_transfer_count == 2


def test_returns_integrated_transfer_count_defaults_given_no_successful_transfers():
    transfers = [
        a_transfer_where_the_sender_reported_an_unrecoverable_error(),
        a_transfer_where_a_copc_triggered_an_error(),
        a_transfer_with_a_final_error(),
    ]
    national_metrics = calculate_national_metrics(transfers)
    assert national_metrics.integrated.transfer_count == 0
    assert national_metrics.integrated.within_3_days == 0
    assert national_metrics.integrated.within_8_days == 0
    assert national_metrics.integrated.beyond_8_days == 0


def test_returns_integrated_transfer_count():
    transfers = [
        an_integrated_transfer(),
        an_integrated_transfer(),
        a_transfer_integrated_beyond_8_days(),
    ]
    national_metrics = calculate_national_metrics(transfers)
    assert national_metrics.integrated.transfer_count == 3


@pytest.mark.parametrize(
    "transfers, expected",
    [
        (
            [a_transfer_integrated_within_3_days()] * 3,
            {"within_3_days": 3, "within_8_days": 0, "beyond_8_days": 0},
        ),
        (
            [a_transfer_integrated_between_3_and_8_days()] * 3,
            {"within_3_days": 0, "within_8_days": 3, "beyond_8_days": 0},
        ),
        (
            [a_transfer_integrated_beyond_8_days()] * 3,
            {"within_3_days": 0, "within_8_days": 0, "beyond_8_days": 3},
        ),
    ],
)
def test_returns_integrated_transfer_count_by_sla_duration(transfers, expected):
    national_metrics = calculate_national_metrics(transfers)
    assert national_metrics.integrated.within_3_days == expected["within_3_days"]
    assert national_metrics.integrated.within_8_days == expected["within_8_days"]
    assert national_metrics.integrated.beyond_8_days == expected["beyond_8_days"]


def test_returns_failed_transfer_count_default_given_no_transfers():
    national_metrics = calculate_national_metrics([])
    assert national_metrics.failed_transfer_count == 0


def test_failed_transfer_count_only_counts_transfers_with_a_final_error():
    transfers = [
        a_transfer_where_the_sender_reported_an_unrecoverable_error(),
        a_transfer_with_a_final_error(),
        a_transfer_where_a_copc_triggered_an_error(),
        a_transfer_with_a_final_error(),
    ]
    national_metrics = calculate_national_metrics(transfers)
    assert national_metrics.failed_transfer_count == 2


def test_returns_pending_transfer_count_default_given_no_transfers():
    transfers: List[Transfer] = []

    national_metrics = calculate_national_metrics(transfers)

    expected_pending_transfer_count = 0

    assert national_metrics.pending_transfer_count == expected_pending_transfer_count


def test_returns_pending_transfer_count_given_only_pending_transfers():
    transfers = [
        a_transfer_that_was_never_integrated(),
        a_transfer_where_the_request_was_never_acknowledged(),
        a_transfer_where_no_core_ehr_was_sent(),
        a_transfer_where_no_copc_continue_was_sent(),
        a_transfer_where_copc_fragments_were_required_but_not_sent(),
        a_transfer_where_copc_fragments_remained_unacknowledged(),
        a_transfer_where_the_sender_reported_an_unrecoverable_error(),
        a_transfer_where_a_copc_triggered_an_error(),
    ]

    national_metrics = calculate_national_metrics(transfers)

    expected_pending_transfer_count = 8

    assert national_metrics.pending_transfer_count == expected_pending_transfer_count


def test_returns_pending_transfer_count_given_a_mixture_of_transfers():
    transfers = [
        a_transfer_that_was_never_integrated(),
        a_transfer_with_a_final_error(),
        an_integrated_transfer(),
    ]

    national_metrics = calculate_national_metrics(transfers)

    expected_pending_transfer_count = 1

    assert national_metrics.pending_transfer_count == expected_pending_transfer_count