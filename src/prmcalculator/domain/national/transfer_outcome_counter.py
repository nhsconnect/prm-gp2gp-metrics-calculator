from typing import List

from prmcalculator.domain.gp2gp.transfer import Transfer, TransferFailureReason


class TransferOutcomeCounter:
    def __init__(self):
        self._transfers: List[Transfer] = []

    @property
    def total(self) -> int:
        return len(self._transfers)

    def count_by_failure_reason(self, failure_reason: TransferFailureReason) -> int:
        transfers_with_failure_reason = [
            transfer.outcome.failure_reason == failure_reason for transfer in self._transfers
        ]
        return sum(transfers_with_failure_reason)

    def add_transfer(self, transfer: Transfer):
        self._transfers.append(transfer)
