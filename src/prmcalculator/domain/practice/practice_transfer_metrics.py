from collections import defaultdict
from typing import Dict, Iterable, List, Optional

from prmcalculator.domain.gp2gp.transfer import Transfer
from prmcalculator.domain.practice.transfer_metrics import TransferMetrics
from prmcalculator.domain.practice.transfer_service import ODSCode, Practice
from prmcalculator.domain.reporting_window import MonthNumber, YearMonth, YearNumber


class PracticeTransferMetrics:
    @classmethod
    def from_group(cls, group: Practice):
        return cls(
            ods_code=group.ods_code,
            name=group.name,
            icb_ods_code=group.icb_ods_code,
            icb_name=group.icb_name,
            transfers=group.transfers,
        )

    def __init__(
        self,
        ods_code: ODSCode,
        name: str,
        icb_ods_code: ODSCode,
        icb_name: Optional[str],
        transfers=Iterable[Transfer],
    ):
        self._ods_code = ods_code
        self._name = name
        self._icb_ods_code = icb_ods_code
        self._icb_name = icb_name
        self._transfers_by_month: Dict[YearMonth, List[Transfer]] = defaultdict(list)

        for transfer in transfers:
            date_requested_tuple = (transfer.date_requested.year, transfer.date_requested.month)
            self._transfers_by_month[date_requested_tuple].append(transfer)

    def monthly_metrics(self, year: YearNumber, month: MonthNumber):
        transfers_in_month = self._transfers_by_month[(year, month)]
        return TransferMetrics(transfers=transfers_in_month)

    @property
    def ods_code(self) -> ODSCode:
        return self._ods_code

    @property
    def name(self) -> str:
        return self._name

    @property
    def icb_ods_code(self) -> ODSCode:
        return self._icb_ods_code

    @property
    def icb_name(self) -> Optional[str]:
        return self._icb_name
