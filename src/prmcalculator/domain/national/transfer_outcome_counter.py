from typing import List

from prmcalculator.domain.gp2gp.transfer import Transfer


class TransferOutcomeCounter:
    _transfers: List[Transfer] = []

    @property
    def total(self) -> int:
        return len(self._transfers)

    def add_transfer(self, transfer: Transfer):
        self._transfers.append(transfer)
