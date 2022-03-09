from typing import Iterable, List, Optional

from prmcalculator.domain.ods_portal.organisation_metadata import CcgMetadata, PracticeMetadata


class PracticeLookup:
    def __init__(self, practices: List[PracticeMetadata], ccgs: List[CcgMetadata]):
        self._practices = practices
        self._asid_to_ods_mapping = {
            asid: practice.ods_code for practice in practices for asid in practice.asids
        }
        self._ods_to_ccg_ods_mapping = {
            practice_ods_code: ccg.ods_code for ccg in ccgs for practice_ods_code in ccg.practices
        }
        self._ods_to_ccg_name_mapping = {
            practice_ods_code: ccg.name for ccg in ccgs for practice_ods_code in ccg.practices
        }

    def all_practices(self) -> Iterable[PracticeMetadata]:
        return iter(self._practices)

    def has_asid_code(self, asid: str) -> bool:
        return asid in self._asid_to_ods_mapping

    def ods_code_from_asid(self, asid: str) -> Optional[str]:
        return self._asid_to_ods_mapping.get(asid)

    def ccg_ods_code_from_practice_ods_code(self, ods_code: str) -> Optional[str]:
        return self._ods_to_ccg_ods_mapping.get(ods_code)

    def ccg_name_from_practice_ods_code(self, ods_code: str) -> Optional[str]:
        return self._ods_to_ccg_name_mapping.get(ods_code)
