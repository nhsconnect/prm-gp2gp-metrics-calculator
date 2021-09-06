from collections import defaultdict
from typing import Iterable, Dict, Tuple, List

from prmcalculator.domain.gp2gp.transfer import Transfer
from prmcalculator.domain.practice.transfer_metrics import TransferMetrics

YearNumber = int
MonthNumber = int
YearMonth = Tuple[YearNumber, MonthNumber]


class PracticeTransferMetrics:
    def __init__(self, ods_code: str, transfers=Iterable[Transfer]):
        self.ods_code = ods_code
        self._transfers_by_month: Dict[YearMonth, List[Transfer]] = defaultdict(list)

        for transfer in transfers:
            date_requested_tuple = (transfer.date_requested.year, transfer.date_requested.month)
            self._transfers_by_month[date_requested_tuple].append(transfer)

    def monthly_metrics(self, year: YearNumber, month: MonthNumber):
        transfers_in_month = self._transfers_by_month[(year, month)]
        return TransferMetrics(transfers=transfers_in_month)
