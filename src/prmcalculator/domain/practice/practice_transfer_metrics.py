from collections import defaultdict
from typing import Iterable, Dict, Tuple, List

from prmcalculator.domain.gp2gp.transfer import Transfer
from prmcalculator.domain.practice.transfer_metrics import TransferMetrics
from prmcalculator.utils.reporting_window import MonthlyReportingWindow


class PracticeTransferMetrics:
    def __init__(
        self, ods_code: str, reporting_window: MonthlyReportingWindow, transfers=Iterable[Transfer]
    ):
        self.ods_code = ods_code
        self._transfers_by_month: Dict[Tuple[int, int], List[Transfer]] = defaultdict(list)
        self.transfer_metrics: Dict[Tuple[int, int], TransferMetrics] = {}

        for metric_month in reporting_window.metric_months:
            self.transfer_metrics[metric_month] = TransferMetrics(transfers=[])

        for transfer in transfers:
            date_requested_tuple = (transfer.date_requested.year, transfer.date_requested.month)
            self._transfers_by_month[date_requested_tuple].append(transfer)

        for month in self._transfers_by_month.keys():
            transfers_in_month = self._transfers_by_month[month]
            self.transfer_metrics[month] = TransferMetrics(transfers=transfers_in_month)
