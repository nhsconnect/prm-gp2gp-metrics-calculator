from prmcalculator.domain.practice.practice_transfer_metrics import PracticeTransferMetrics
from tests.builders.common import a_datetime
from tests.builders.gp2gp import (
    a_transfer_integrated_within_3_days,
    a_transfer_integrated_beyond_8_days,
)


def test_returns_transfer_metrics():
    transfers = [
        a_transfer_integrated_beyond_8_days(
            date_requested=a_datetime(year=2021, month=7),
        ),
        a_transfer_integrated_within_3_days(
            date_requested=a_datetime(year=2021, month=8),
        ),
        a_transfer_integrated_beyond_8_days(
            date_requested=a_datetime(year=2021, month=8),
        ),
    ]

    practice_transfers = PracticeTransferMetrics(transfers)

    july_transfer_metrics = practice_transfers.monthly_metrics(2021, 7)
    aug_transfer_metrics = practice_transfers.monthly_metrics(2021, 8)

    assert july_transfer_metrics.integrated_total() == 1
    assert july_transfer_metrics.integrated_within_3_days() == 0
    assert july_transfer_metrics.integrated_beyond_8_days() == 1
    assert aug_transfer_metrics.integrated_total() == 2
    assert aug_transfer_metrics.integrated_within_3_days() == 1
    assert aug_transfer_metrics.integrated_beyond_8_days() == 1
