from prmcalculator.domain.practice.transfer_metrics import TransferMetrics
from tests.builders.gp2gp import (
    a_transfer_integrated_between_3_and_8_days,
    a_transfer_integrated_beyond_8_days,
    a_transfer_integrated_within_3_days,
    a_transfer_that_was_never_integrated,
    a_transfer_where_a_copc_triggered_an_error,
    a_transfer_where_copc_fragments_remained_unacknowledged,
    a_transfer_where_copc_fragments_were_required_but_not_sent,
    a_transfer_where_no_copc_continue_was_sent,
    a_transfer_where_no_core_ehr_was_sent,
    a_transfer_where_the_request_was_never_acknowledged,
    a_transfer_where_the_sender_reported_an_unrecoverable_error,
    a_transfer_with_a_final_error,
)


def test_returns_process_failure_not_integrated_total():
    transfers = [
        a_transfer_integrated_between_3_and_8_days(),
        a_transfer_with_a_final_error(),
        a_transfer_where_the_request_was_never_acknowledged(),
        a_transfer_where_no_core_ehr_was_sent(),
        a_transfer_that_was_never_integrated(),
        a_transfer_integrated_beyond_8_days(),
        a_transfer_where_a_copc_triggered_an_error(),
    ]

    transfer_metrics = TransferMetrics(transfers=transfers)

    assert transfer_metrics.process_failure_not_integrated() == 1


def test_returns_integrated_total():
    transfers = [
        a_transfer_integrated_between_3_and_8_days(),
        a_transfer_with_a_final_error(),
        a_transfer_where_the_request_was_never_acknowledged(),
        a_transfer_where_no_core_ehr_was_sent(),
        a_transfer_that_was_never_integrated(),
        a_transfer_integrated_beyond_8_days(),
        a_transfer_where_a_copc_triggered_an_error(),
    ]

    transfer_metrics = TransferMetrics(transfers=transfers)

    assert transfer_metrics.integrated_total() == 2


def test_returns_integrated_within_3_days():
    transfers = [
        a_transfer_integrated_within_3_days(),
        a_transfer_integrated_within_3_days(),
        a_transfer_integrated_within_3_days(),
        a_transfer_integrated_between_3_and_8_days(),
        a_transfer_with_a_final_error(),
        a_transfer_where_the_request_was_never_acknowledged(),
        a_transfer_where_no_core_ehr_was_sent(),
        a_transfer_that_was_never_integrated(),
        a_transfer_integrated_beyond_8_days(),
        a_transfer_where_a_copc_triggered_an_error(),
    ]

    transfer_metrics = TransferMetrics(transfers=transfers)

    assert transfer_metrics.integrated_within_3_days() == 3


def test_returns_integrated_within_8_days():
    transfers = [
        a_transfer_integrated_within_3_days(),
        a_transfer_integrated_between_3_and_8_days(),
        a_transfer_integrated_between_3_and_8_days(),
        a_transfer_with_a_final_error(),
        a_transfer_where_the_request_was_never_acknowledged(),
        a_transfer_where_no_core_ehr_was_sent(),
        a_transfer_that_was_never_integrated(),
        a_transfer_integrated_beyond_8_days(),
        a_transfer_where_a_copc_triggered_an_error(),
    ]

    transfer_metrics = TransferMetrics(transfers=transfers)

    assert transfer_metrics.integrated_within_8_days() == 2


def test_returns_integrated_beyond_8_days():
    transfers = [
        a_transfer_integrated_within_3_days(),
        a_transfer_integrated_between_3_and_8_days(),
        a_transfer_with_a_final_error(),
        a_transfer_where_the_request_was_never_acknowledged(),
        a_transfer_where_no_core_ehr_was_sent(),
        a_transfer_that_was_never_integrated(),
        a_transfer_integrated_beyond_8_days(),
        a_transfer_integrated_beyond_8_days(),
        a_transfer_integrated_beyond_8_days(),
        a_transfer_integrated_beyond_8_days(),
        a_transfer_where_a_copc_triggered_an_error(),
    ]

    transfer_metrics = TransferMetrics(transfers=transfers)

    assert transfer_metrics.integrated_beyond_8_days() == 4


def test_returns_received_by_practice_total():
    transfers = [
        a_transfer_integrated_within_3_days(),
        a_transfer_integrated_between_3_and_8_days(),
        a_transfer_integrated_between_3_and_8_days(),
        a_transfer_with_a_final_error(),
        a_transfer_where_the_request_was_never_acknowledged(),
        a_transfer_where_no_core_ehr_was_sent(),
        a_transfer_that_was_never_integrated(),
        a_transfer_integrated_beyond_8_days(),
        a_transfer_where_a_copc_triggered_an_error(),
    ]

    transfer_metrics = TransferMetrics(transfers=transfers)

    assert transfer_metrics.received_by_practice_total() == 5


def test_returns_received_by_practice_percent_of_requested():
    transfers = [
        a_transfer_integrated_within_3_days(),
        a_transfer_integrated_between_3_and_8_days(),
        a_transfer_integrated_between_3_and_8_days(),
        a_transfer_with_a_final_error(),
        a_transfer_where_the_request_was_never_acknowledged(),
        a_transfer_where_no_core_ehr_was_sent(),
        a_transfer_that_was_never_integrated(),
        a_transfer_integrated_beyond_8_days(),
        a_transfer_where_a_copc_triggered_an_error(),
    ]

    transfer_metrics = TransferMetrics(transfers=transfers)

    assert transfer_metrics.received_by_practice_percent_of_requested() == 55.56


def test_returns_requested_by_practice_total():
    transfers = [
        a_transfer_integrated_within_3_days(),
        a_transfer_integrated_between_3_and_8_days(),
        a_transfer_integrated_between_3_and_8_days(),
        a_transfer_with_a_final_error(),
        a_transfer_where_the_request_was_never_acknowledged(),
        a_transfer_where_no_core_ehr_was_sent(),
        a_transfer_that_was_never_integrated(),
        a_transfer_integrated_beyond_8_days(),
        a_transfer_where_a_copc_triggered_an_error(),
    ]

    transfer_metrics = TransferMetrics(transfers=transfers)

    assert transfer_metrics.requested_by_practice_total() == 9


def test_returns_technical_failures_total():
    transfers = [
        a_transfer_integrated_within_3_days(),
        a_transfer_with_a_final_error(),
        a_transfer_where_the_request_was_never_acknowledged(),
        a_transfer_where_no_core_ehr_was_sent(),
        a_transfer_where_no_copc_continue_was_sent(),
        a_transfer_where_copc_fragments_were_required_but_not_sent(),
        a_transfer_where_copc_fragments_remained_unacknowledged(),
        a_transfer_where_the_sender_reported_an_unrecoverable_error(),
        a_transfer_that_was_never_integrated(),
        a_transfer_where_a_copc_triggered_an_error(),
    ]

    transfer_metrics = TransferMetrics(transfers=transfers)

    assert transfer_metrics.technical_failures_total() == 7


def test_returns_unclassified_failure_total():
    transfers = [a_transfer_where_a_copc_triggered_an_error()]

    transfer_metrics = TransferMetrics(transfers=transfers)

    assert transfer_metrics.unclassified_failure_total() == 1
