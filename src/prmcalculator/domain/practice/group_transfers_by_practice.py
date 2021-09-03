from typing import List, Dict

from prmcalculator.domain.gp2gp.transfer import Transfer
from prmcalculator.domain.practice.practice_lookup import PracticeLookup


def group_transfers_by_practice(
    transfers: List[Transfer], practice_lookup: PracticeLookup, observability_probe
) -> Dict[str, List[Transfer]]:
    practice_transfers: Dict[str, List[Transfer]] = {
        ods_code: [] for ods_code in practice_lookup.all_ods_codes()
    }
    unexpected_asids = set()

    for transfer in transfers:
        requesting_practice_asid = transfer.requesting_practice.asid
        if practice_lookup.has_asid_code(requesting_practice_asid):
            ods_code = practice_lookup.ods_code_from_asid(requesting_practice_asid)
            practice_transfers[ods_code].append(transfer)
        else:
            unexpected_asids.add(requesting_practice_asid)

    if len(unexpected_asids) > 0:
        observability_probe.unexpected_asid_count(unexpected_asids)

    return practice_transfers
