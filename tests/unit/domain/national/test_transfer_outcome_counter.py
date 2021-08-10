from prmcalculator.domain.gp2gp.transfer import TransferFailureReason
from prmcalculator.domain.national.transfer_outcome_counter import TransferOutcomeCounter
from tests.builders.gp2gp import (
    build_transfer,
    a_transfer_integrated_beyond_8_days,
    a_transfer_that_was_never_integrated,
    a_transfer_with_a_final_error,
)


def test_returns_total_count_of_transfers():
    a_transfer = build_transfer()

    counter = TransferOutcomeCounter()
    counter.add_transfer(a_transfer)
    counter.add_transfer(a_transfer)

    actual = counter.total
    expected = 2

    assert actual == expected


def test_returns_total_0_when_no_transfers_added():
    counter = TransferOutcomeCounter()

    actual = counter.total
    expected = 0

    assert actual == expected


def test_returns_total_count_by_failure_reason():
    a_failed_transfer = a_transfer_with_a_final_error()
    a_non_integrated_transfer = a_transfer_that_was_never_integrated()
    an_integrated_late_transfer = a_transfer_integrated_beyond_8_days()

    counter = TransferOutcomeCounter()
    counter.add_transfer(a_failed_transfer)
    counter.add_transfer(a_non_integrated_transfer)
    counter.add_transfer(an_integrated_late_transfer)
    counter.add_transfer(an_integrated_late_transfer)
    counter.add_transfer(an_integrated_late_transfer)

    actual = counter.count_by_failure_reason(TransferFailureReason.INTEGRATED_LATE)
    expected = 3

    assert actual == expected


def test_returns_total_count_by_failure_reason_0_when_no_transfers_added():
    counter = TransferOutcomeCounter()

    actual = counter.count_by_failure_reason(TransferFailureReason.INTEGRATED_LATE)
    expected = 0

    assert actual == expected
