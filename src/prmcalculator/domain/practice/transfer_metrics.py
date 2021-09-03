from collections import Counter
from typing import Iterable

from prmcalculator.domain.gp2gp.sla import SlaCounter
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
        self._sla_counter: SlaCounter = SlaCounter()

        for transfer in transfers:
            self._counts_by_outcome.update([transfer.outcome])
            self._counts_by_status.update([transfer.outcome.status])
            if transfer.outcome.status == TransferStatus.INTEGRATED_ON_TIME:
                self._sla_counter.increment(transfer.sla_duration)

    def process_failure_not_integrated(self) -> int:
        return self._counts_by_outcome[_NOT_INTEGRATED]

    def integrated_total(self) -> int:
        return (
            self._counts_by_outcome[_INTEGRATED_LATE]
            + self._counts_by_status[TransferStatus.INTEGRATED_ON_TIME]
        )

    def integrated_within_3_days(self) -> int:
        return self._sla_counter.within_3_days

    def integrated_within_8_days(self) -> int:
        return self._sla_counter.within_8_days

    def integrated_beyond_8_days(self) -> int:
        return self._counts_by_outcome[_INTEGRATED_LATE]

    def received_by_practice_total(self) -> int:
        return self.integrated_total() + self.process_failure_not_integrated()

    def requested_by_practice_total(self) -> int:
        return sum(self._counts_by_outcome.values())
