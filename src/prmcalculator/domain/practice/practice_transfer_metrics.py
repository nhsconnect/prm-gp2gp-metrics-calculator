from collections import defaultdict
from typing import Iterable, Dict, Tuple, List

from prmcalculator.domain.gp2gp.transfer import Transfer
from prmcalculator.domain.practice.transfer_metrics import TransferMetrics
from prmcalculator.utils.reporting_window import MonthlyReportingWindow


class PracticeTransferMetrics:
    def __init__(self, reporting_window: MonthlyReportingWindow, transfers=Iterable[Transfer]):
        self._transfers_by_month: Dict[Tuple[int, int], List[Transfer]] = defaultdict(list)
        self.transfer_metrics: Dict[Tuple[int, int], TransferMetrics] = {}

        for transfer in transfers:
            date_requested_tuple = (transfer.date_requested.year, transfer.date_requested.month)
            self._transfers_by_month[date_requested_tuple].append(transfer)

        for metric_month in reporting_window.metric_months:
            transfers_in_month = self._transfers_by_month[metric_month]
            self.transfer_metrics[metric_month] = TransferMetrics(transfers=transfers_in_month)