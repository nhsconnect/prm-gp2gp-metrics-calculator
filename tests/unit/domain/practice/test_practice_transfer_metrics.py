from prmcalculator.domain.practice.practice_transfer_metrics import PracticeTransferMetrics
from prmcalculator.domain.practice.transfer_metrics import TransferMetrics
from prmcalculator.utils.reporting_window import MonthlyReportingWindow
from tests.builders.common import a_datetime
from tests.builders.gp2gp import build_transfer


def test_returns_transfer_metrics():
    an_aug_transfer = build_transfer(date_requested=a_datetime(year=2021, month=8))
    a_july_transfer = build_transfer(date_requested=a_datetime(year=2021, month=7))
    transfers = [an_aug_transfer, an_aug_transfer, a_july_transfer]
    reporting_window = MonthlyReportingWindow.prior_to(
        date_anchor=a_datetime(year=2020, month=9), number_of_months=1
    )

    practice_transfers = PracticeTransferMetrics(
        transfers=transfers, reporting_window=reporting_window
    )

    actual_transfer_metrics = practice_transfers.transfer_metrics

    assert type(actual_transfer_metrics[(2021, 8)]) == TransferMetrics
    assert type(actual_transfer_metrics[(2021, 7)]) == TransferMetrics
    assert actual_transfer_metrics.keys() >= {(2021, 8), (2021, 7)}
