from prmcalculator.domain.gp2gp.transfer import Practice
from prmcalculator.domain.practice.practice_transfer_metrics import PracticeTransferMetrics
from prmcalculator.domain.practice.transfer_metrics import TransferMetrics
from prmcalculator.utils.reporting_window import MonthlyReportingWindow
from tests.builders.common import a_string, a_datetime
from tests.builders.gp2gp import build_transfer


def test_returns_ods_code():
    ods_code = "A1234"
    a_transfer = build_transfer(
        requesting_practice=Practice(asid=a_string(12), supplier=a_string(12))
    )
    reporting_window = MonthlyReportingWindow.prior_to(
        date_anchor=a_datetime(year=2020, month=1), number_of_months=1
    )

    practice_transfers = PracticeTransferMetrics(
        ods_code=ods_code, transfers=[a_transfer], reporting_window=reporting_window
    )

    actual_ods_code = practice_transfers.ods_code

    assert actual_ods_code == ods_code


def test_returns_transfer_metrics():
    an_aug_transfer = build_transfer(date_requested=a_datetime(year=2021, month=8))
    a_july_transfer = build_transfer(date_requested=a_datetime(year=2021, month=7))
    transfers = [an_aug_transfer, an_aug_transfer, a_july_transfer]
    reporting_window = MonthlyReportingWindow.prior_to(
        date_anchor=a_datetime(year=2020, month=9), number_of_months=1
    )

    practice_transfers = PracticeTransferMetrics(
        ods_code=a_string(), transfers=transfers, reporting_window=reporting_window
    )

    actual_transfer_metrics = practice_transfers.transfer_metrics

    assert type(actual_transfer_metrics[(2021, 8)]) == TransferMetrics
    assert type(actual_transfer_metrics[(2021, 7)]) == TransferMetrics
    assert actual_transfer_metrics.keys() >= {(2021, 8), (2021, 7)}
