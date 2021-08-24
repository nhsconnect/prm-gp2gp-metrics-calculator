from collections import defaultdict
from typing import List, Dict

from prmcalculator.domain.gp2gp.transfer import Transfer
from prmcalculator.domain.practice.practice_lookup import PracticeLookup


def create_practice_transfer_mapping(
    transfers: List[Transfer], practice_lookup: PracticeLookup
) -> Dict[str, List[Transfer]]:
    practice_transfers = defaultdict(list)

    for transfer in transfers:
        transfer_ods_code = practice_lookup.ods_code_from_asid(transfer.requesting_practice.asid)
        practice_transfers[transfer_ods_code].append(transfer)

    return practice_transfers
