from unittest import mock

from prmcalculator.domain.national.metrics_calculator import calculate_national_metrics_month
from prmcalculator.domain.national.transfer_outcomes import TransferOutcomes
from tests.builders.gp2gp import build_transfer


def test_returns_0_total_default_given_no_transfers():
    national_metrics_month = calculate_national_metrics_month(transfers=[], year=2020, month=1)
    assert national_metrics_month.total == 0


def test_returns_1_total_default_given_1_transfer():
    a_transfer = build_transfer()

    national_metrics_month = calculate_national_metrics_month(
        transfers=[a_transfer], year=2020, month=1
    )
    assert national_metrics_month.total == 1


def test_returns_year_and_month():
    national_metrics_month = calculate_national_metrics_month(transfers=[], year=2020, month=1)
    assert national_metrics_month.year == 2020
    assert national_metrics_month.month == 1


def test_calls_transfer_outcomes_group_transfer_with_transfers():
    transfers = [build_transfer()]

    with mock.patch.object(TransferOutcomes, "group_transfers") as mock_transfer_outcomes:
        calculate_national_metrics_month(transfers=transfers, year=2020, month=1)

    mock_transfer_outcomes.assert_called_once_with(transfers)


def test_returns_transfer_outcomes_given_transfers():
    transfers = [build_transfer()]

    national_metrics_month = calculate_national_metrics_month(
        transfers=transfers, year=2020, month=1
    )

    assert isinstance(national_metrics_month.transfer_outcomes, TransferOutcomes)
