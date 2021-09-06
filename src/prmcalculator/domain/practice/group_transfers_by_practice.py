from typing import List, Dict

from prmcalculator.domain.gp2gp.transfer import Transfer
from prmcalculator.domain.ods_portal.organisation_metadata import PracticeDetails
from prmcalculator.domain.practice.practice_lookup import PracticeLookup
from prmcalculator.domain.practice.practice_transfer_metrics import PracticeTransferMetrics


class TransferAccumulator:
    def __init__(self, practice: PracticeDetails):
        self._name = practice.name
        self._ods_code = practice.ods_code
        self._transfers: List[Transfer] = []

    def add_transfer(self, transfer: Transfer):
        self._transfers.append(transfer)

    def into_metrics(self) -> PracticeTransferMetrics:
        return PracticeTransferMetrics(
            ods_code=self._ods_code, name=self._name, transfers=self._transfers
        )


def group_transfers_by_practice(
    transfers: List[Transfer], practice_lookup: PracticeLookup, observability_probe
) -> Dict[str, PracticeTransferMetrics]:
    practice_transfers: Dict[str, TransferAccumulator] = {
        practice.ods_code: TransferAccumulator(practice)
        for practice in practice_lookup.all_practices()
    }
    for transfer in transfers:
        requesting_practice_asid = transfer.requesting_practice.asid
        if practice_lookup.has_asid_code(requesting_practice_asid):
            ods_code = practice_lookup.ods_code_from_asid(requesting_practice_asid)
            practice_transfers[ods_code].add_transfer(transfer)
        else:
            observability_probe.record_unknown_practice_for_transfer(transfer)

    return {
        ods_code: accumulator.into_metrics() for ods_code, accumulator in practice_transfers.items()
    }
