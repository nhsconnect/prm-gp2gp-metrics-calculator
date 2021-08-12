from dataclasses import dataclass, field
from typing import List

from prmcalculator.domain.gp2gp.transfer import Transfer, TransferFailureReason


@dataclass
class TransferCounter:
    transfers: List[Transfer] = field(default_factory=list)

    @property
    def total(self) -> int:
        return len(self.transfers)


@dataclass
class TransferOutcomeCounter(TransferCounter):
    def count_by_failure_reason(self, failure_reason: TransferFailureReason) -> int:
        transfers_with_failure_reason = [
            transfer.outcome.failure_reason == failure_reason for transfer in self.transfers
        ]
        return sum(transfers_with_failure_reason)

    def add_transfer(self, transfer: Transfer):
        self.transfers.append(transfer)
