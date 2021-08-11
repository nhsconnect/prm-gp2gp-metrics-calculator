from typing import List

from prmcalculator.domain.gp2gp.transfer import Transfer
from prmcalculator.domain.national.transfer_outcomes import TransferOutcomes


class NationalMetricsMonth:
    def __init__(self, transfers: List[Transfer], year: int, month: int):
        self._year = year
        self._month = month
        self._transfers = transfers
        self._transfer_outcomes = TransferOutcomes.group_transfers(transfers)

    @property
    def total(self) -> int:
        return len(self._transfers)

    @property
    def year(self) -> int:
        return self._year

    @property
    def month(self) -> int:
        return self._month

    @property
    def transfer_outcomes(self) -> TransferOutcomes:
        return self._transfer_outcomes


def calculate_national_metrics_month(
    transfers: List[Transfer], year: int, month: int
) -> NationalMetricsMonth:
    return NationalMetricsMonth(transfers, year, month)
