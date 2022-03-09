from random import randrange

from prmcalculator.domain.ods_portal.organisation_metadata import PracticeMetadata
from tests.builders.common import a_string


def an_asid_list():
    return [a_string() for _ in range(randrange(1, 3))]


def build_practice_details(**kwargs) -> PracticeMetadata:
    return PracticeMetadata(
        ods_code=kwargs.get("ods_code", a_string()),
        name=kwargs.get("name", a_string()),
        asids=kwargs.get("asids", an_asid_list()),
    )
