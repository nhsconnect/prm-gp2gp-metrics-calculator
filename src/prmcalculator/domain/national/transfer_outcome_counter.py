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
    def failure_reason(self, failure_reason: TransferFailureReason) -> TransferCounter:
        transfers_with_failure_reason = [
            transfer
            for transfer in self.transfers
            if transfer.outcome.failure_reason == failure_reason
        ]
        return TransferCounter(transfers_with_failure_reason)

    def add_transfer(self, transfer: Transfer):
        self.transfers.append(transfer)
