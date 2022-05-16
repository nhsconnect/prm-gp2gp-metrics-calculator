from dataclasses import dataclass
from typing import Dict, List, Optional, Tuple

from prmcalculator.domain.gp2gp.transfer import Transfer
from prmcalculator.domain.ods_portal.organisation_lookup import OrganisationLookup
from prmcalculator.domain.ods_portal.organisation_metadata import PracticeMetadata

ODSCode = Optional[str]


@dataclass(frozen=True)
class PracticeTransfersDeprecated:
    ods_code: ODSCode
    name: str
    transfers: Tuple[Transfer, ...]
    ccg_ods_code: ODSCode
    ccg_name: Optional[str]


class TransferAccumulatorDeprecated:
    def __init__(self, practice: PracticeMetadata):
        self._ods_code = practice.ods_code
        self._name = practice.name
        self._transfers: List[Transfer] = []

    def add_transfer(self, transfer: Transfer):
        self._transfers.append(transfer)

    def into_group(self) -> PracticeTransfersDeprecated:
        return PracticeTransfersDeprecated(
            ods_code=self._ods_code,
            name=self._name,
            transfers=tuple(self._transfers),
            ccg_ods_code=None,
            ccg_name=None,
        )


def group_transfers_by_practice_deprecated(
    transfers: List[Transfer], organisation_lookup: OrganisationLookup, observability_probe
) -> List[PracticeTransfersDeprecated]:
    practice_transfers: Dict[ODSCode, TransferAccumulatorDeprecated] = {
        practice.ods_code: TransferAccumulatorDeprecated(practice)
        for practice in organisation_lookup.all_practices()
    }
    for transfer in transfers:
        requesting_practice_asid = transfer.requesting_practice.asid
        if organisation_lookup.has_asid_code(requesting_practice_asid):
            ods_code = organisation_lookup.ods_code_from_asid(requesting_practice_asid)
            practice_transfers[ods_code].add_transfer(transfer)
        else:
            observability_probe.record_unknown_practice_for_transfer(transfer)
    return [accumulator.into_group() for accumulator in practice_transfers.values()]
