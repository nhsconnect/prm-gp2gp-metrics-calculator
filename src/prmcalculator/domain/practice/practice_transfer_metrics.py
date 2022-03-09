from collections import defaultdict
from typing import Dict, Iterable, List, Optional

from prmcalculator.domain.gp2gp.transfer import Transfer
from prmcalculator.domain.practice.group_transfers_by_practice import PracticeTransfers
from prmcalculator.domain.practice.transfer_metrics import TransferMetrics
from prmcalculator.domain.reporting_window import MonthNumber, YearMonth, YearNumber


class PracticeTransferMetrics:
    @classmethod
    def from_group(cls, group: PracticeTransfers):
        return cls(
            # ccg_ods_code needs to be populated
            ods_code=group.ods_code,
            name=group.name,
            ccg_ods_code=None,
            transfers=group.transfers,
        )

    def __init__(
        self, ods_code: str, name: str, ccg_ods_code: Optional[str], transfers=Iterable[Transfer]
    ):
        self._ods_code = ods_code
        self._name = name
        self._ccg_ods_code = ccg_ods_code
        self._transfers_by_month: Dict[YearMonth, List[Transfer]] = defaultdict(list)

        for transfer in transfers:
            date_requested_tuple = (transfer.date_requested.year, transfer.date_requested.month)
            self._transfers_by_month[date_requested_tuple].append(transfer)

    def monthly_metrics(self, year: YearNumber, month: MonthNumber):
        transfers_in_month = self._transfers_by_month[(year, month)]
        return TransferMetrics(transfers=transfers_in_month)

    @property
    def ods_code(self) -> str:
        return self._ods_code

    @property
    def name(self) -> str:
        return self._name

    @property
    def ccg_ods_code(self) -> Optional[str]:
        return self._ccg_ods_code
