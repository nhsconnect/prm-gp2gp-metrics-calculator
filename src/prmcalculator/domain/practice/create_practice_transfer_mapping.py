from collections import defaultdict
from warnings import warn
from typing import List, Dict

from prmcalculator.domain.gp2gp.transfer import Transfer
from prmcalculator.domain.practice.practice_lookup import PracticeLookup


def create_practice_transfer_mapping(
    transfers: List[Transfer], practice_lookup: PracticeLookup
) -> Dict[str, List[Transfer]]:
    practice_transfers = defaultdict(list)
    unexpected_asids = set()

    for transfer in transfers:
        requesting_practice_asid = transfer.requesting_practice.asid
        if practice_lookup.has_asid_code(requesting_practice_asid):
            ods_code = practice_lookup.ods_code_from_asid(transfer.requesting_practice.asid)
            practice_transfers[ods_code].append(transfer)
        else:
            unexpected_asids.add(requesting_practice_asid)

    if len(unexpected_asids) > 0:
        warn(f"Unexpected ASID count: {len(unexpected_asids)}", RuntimeWarning)

    return practice_transfers
