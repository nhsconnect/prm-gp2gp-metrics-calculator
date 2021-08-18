from collections import defaultdict
from typing import List

from prmcalculator.domain.gp2gp.transfer import Transfer
from prmcalculator.domain.practice.practice_lookup import PracticeLookup
from prmcalculator.domain.practice.practice_transfer_metrics import PracticeTransferMetrics


def construct_practice_transfer_metrics(transfers: List[Transfer], practice_lookup: PracticeLookup):
    _practice_transfers = defaultdict(list)
    practice_transfer_metrics = {}

    for transfer in transfers:
        transfer_ods_code = practice_lookup.ods_code_from_asid(transfer.requesting_practice.asid)
        _practice_transfers[transfer_ods_code].append(transfer)

    for practice_ods_code in _practice_transfers.keys():
        transfers = _practice_transfers[practice_ods_code]
        practice_transfer_metrics[practice_ods_code] = PracticeTransferMetrics(
            ods_code=practice_ods_code, transfers=transfers
        )

    return practice_transfer_metrics
