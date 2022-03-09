from typing import Iterable, List

from prmcalculator.domain.ods_portal.organisation_metadata import PracticeMetadata


class PracticeLookup:
    def __init__(self, practices: List[PracticeMetadata]):
        self._practices = practices
        self._asid_to_ods_mapping = {
            asid: practice.ods_code for practice in practices for asid in practice.asids
        }

    def all_practices(self) -> Iterable[PracticeMetadata]:
        return iter(self._practices)

    def has_asid_code(self, asid):
        return asid in self._asid_to_ods_mapping

    def ods_code_from_asid(self, asid):
        return self._asid_to_ods_mapping.get(asid)
