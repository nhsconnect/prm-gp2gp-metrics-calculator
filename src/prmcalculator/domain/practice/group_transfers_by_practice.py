from dataclasses import dataclass
from typing import Dict, List

from prmcalculator.domain.gp2gp.transfer import Transfer

ODSCode = str


@dataclass(frozen=True)
class Practice:
    ods_code: ODSCode
    name: str
    transfers: List[Transfer]
    ccg_ods_code: ODSCode
    ccg_name: str


class PracticeTransfers:
    ods_code: List[Transfer]


def group_transfers_by_practice(transfers: List[Transfer], observability_probe) -> List[Practice]:

    practice_transfers_by_ods = _group_practice_transfers_by_ods_code(transfers)

    practice_list = []
    for practice_transfers in practice_transfers_by_ods.values():
        latest_transfer = practice_transfers[0]
        for transfer in practice_transfers:
            if transfer.date_requested > latest_transfer.date_requested:
                latest_transfer = transfer

        practice_list.append(
            Practice(
                ods_code=latest_transfer.requesting_practice.ods_code,
                name=latest_transfer.requesting_practice.name,
                ccg_ods_code=latest_transfer.requesting_practice.ccg_ods_code,
                ccg_name=latest_transfer.requesting_practice.ccg_name,
                transfers=practice_transfers,
            )
        )

    return practice_list
    # log errors:
    # observability_probe.record_unknown_practice_for_transfer(transfer)


PracticeTransfersDictByOds = Dict[ODSCode, List[Transfer]]


def _group_practice_transfers_by_ods_code(transfers: List[Transfer]) -> PracticeTransfersDictByOds:
    practice_transfers: PracticeTransfersDictByOds = {}
    for transfer in transfers:
        if transfer.requesting_practice.ods_code not in practice_transfers:
            practice_transfers[transfer.requesting_practice.ods_code] = []
        practice_transfers[transfer.requesting_practice.ods_code].append(transfer)
    return practice_transfers
