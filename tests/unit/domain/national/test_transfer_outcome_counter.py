from prmcalculator.domain.national.transfer_outcome_counter import TransferOutcomeCounter
from tests.builders.gp2gp import build_transfer


def test_returns_total_count_of_transfers():
    a_transfer = build_transfer()

    counter = TransferOutcomeCounter()
    counter.add_transfer(a_transfer)
    counter.add_transfer(a_transfer)

    actual = counter.total
    expected = 2

    assert actual == expected
