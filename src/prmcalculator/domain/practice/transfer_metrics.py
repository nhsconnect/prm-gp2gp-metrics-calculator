from collections import Counter
from typing import Iterable

from prmcalculator.domain.gp2gp.transfer import (
    Transfer,
    TransferOutcome,
    TransferStatus,
    TransferFailureReason,
)

_NOT_INTEGRATED = TransferOutcome(
    TransferStatus.PROCESS_FAILURE, TransferFailureReason.TRANSFERRED_NOT_INTEGRATED
)

_INTEGRATED_LATE = TransferOutcome(
    TransferStatus.PROCESS_FAILURE, TransferFailureReason.INTEGRATED_LATE
)


class TransferMetrics:
    def __init__(self, transfers: Iterable[Transfer]):
        self._counts_by_outcome: Counter[TransferOutcome] = Counter()
        self._counts_by_status: Counter[TransferStatus] = Counter()

        for transfer in transfers:
            self._counts_by_outcome.update([transfer.outcome])
            self._counts_by_status.update([transfer.outcome.status])

    def process_failure_not_integrated(self) -> int:
        return self._counts_by_outcome[_NOT_INTEGRATED]

    def integrated_total(self) -> int:
        return (
            self._counts_by_outcome[_INTEGRATED_LATE]
            + self._counts_by_status[TransferStatus.INTEGRATED_ON_TIME]
        )
