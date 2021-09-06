from typing import List, Dict

from prmcalculator.domain.gp2gp.transfer import Transfer
from prmcalculator.domain.practice.practice_lookup import PracticeLookup
from prmcalculator.domain.practice.practice_transfer_metrics import PracticeTransferMetrics


def group_transfers_by_practice(
    transfers: List[Transfer], practice_lookup: PracticeLookup, observability_probe
) -> Dict[str, PracticeTransferMetrics]:
    practice_transfers: Dict[str, List[Transfer]] = {
        ods_code: [] for ods_code in practice_lookup.all_ods_codes()
    }

    for transfer in transfers:
        requesting_practice_asid = transfer.requesting_practice.asid
        if practice_lookup.has_asid_code(requesting_practice_asid):
            ods_code = practice_lookup.ods_code_from_asid(requesting_practice_asid)
            practice_transfers[ods_code].append(transfer)
        else:
            observability_probe.record_unknown_practice_for_transfer(transfer)

    return {
        ods_code: PracticeTransferMetrics(ods_code, transfers)
        for ods_code, transfers in practice_transfers.items()
    }
