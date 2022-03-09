from random import randrange

from prmcalculator.domain.ods_portal.organisation_metadata import CcgMetadata, PracticeMetadata
from tests.builders.common import a_string


def _a_list_of_strings():
    return [a_string() for _ in range(randrange(1, 3))]


def build_practice_metadata(**kwargs) -> PracticeMetadata:
    return PracticeMetadata(
        ods_code=kwargs.get("ods_code", a_string()),
        name=kwargs.get("name", a_string()),
        asids=kwargs.get("asids", _a_list_of_strings()),
    )


def build_ccg_metadata(**kwargs) -> CcgMetadata:
    return CcgMetadata(
        ods_code=kwargs.get("ods_code", a_string()),
        name=kwargs.get("name", a_string()),
        practices=kwargs.get("practices", _a_list_of_strings()),
    )
