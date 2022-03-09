from typing import List

from prmcalculator.domain.ods_portal.organisation_lookup import OrganisationLookup
from prmcalculator.domain.ods_portal.organisation_metadata import PracticeMetadata
from tests.builders.common import a_string
from tests.builders.ods_portal import build_ccg_metadata, build_practice_metadata


def test_all_practices_returns_nothing_given_no_practices():
    practices: List[PracticeMetadata] = []
    organisation_lookup = OrganisationLookup(practices, ccgs=[])

    expected: List[PracticeMetadata] = []

    actual = list(organisation_lookup.all_practices())

    assert actual == expected


def test_all_practices_returns_practices():
    practice_one = build_practice_metadata()
    practice_two = build_practice_metadata()

    practices = [practice_one, practice_two]

    organisation_lookup = OrganisationLookup(practices, ccgs=[])

    expected = [practice_one, practice_two]

    actual = list(organisation_lookup.all_practices())

    assert actual == expected


def test_has_asid_code_returns_false_given_no_matching_practice():
    practices = [build_practice_metadata(asids=["123"])]

    organisation_lookup = OrganisationLookup(practices, ccgs=[])

    expected = False

    actual = organisation_lookup.has_asid_code("456")

    assert actual == expected


def test_has_asid_code_returns_true_given_a_matching_practice():
    practices = [build_practice_metadata(asids=["123"])]

    organisation_lookup = OrganisationLookup(practices, ccgs=[])

    expected = True

    actual = organisation_lookup.has_asid_code("123")

    assert actual == expected


def test_has_asid_code_returns_true_given_a_matching_practice_with_multiple_asid():
    practices = [build_practice_metadata(asids=["123", "456"])]

    organisation_lookup = OrganisationLookup(practices, ccgs=[])

    expected = True

    actual = organisation_lookup.has_asid_code("456")

    assert actual == expected


def test_has_asid_code_returns_true_given_multiple_practices():
    practices = [build_practice_metadata(asids=["123"]), build_practice_metadata(asids=["456"])]

    organisation_lookup = OrganisationLookup(practices, ccgs=[])

    expected = True

    actual = organisation_lookup.has_asid_code("456")

    assert actual == expected


def test_ods_code_from_asid_returns_none_given_no_practices():
    practices: List[PracticeMetadata] = []
    organisation_lookup = OrganisationLookup(practices, ccgs=[])

    expected = None

    actual = organisation_lookup.ods_code_from_asid("123")

    assert actual == expected


def test_ods_code_from_asid_returns_matching_practice_given_practice_with_a_single_asid():
    practice = build_practice_metadata(asids=["123"], ods_code="ABC")
    organisation_lookup = OrganisationLookup(practices=[practice], ccgs=[])

    expected = "ABC"

    actual = organisation_lookup.ods_code_from_asid("123")

    assert actual == expected


def test_ods_code_from_asid_returns_matching_practice_given_practice_with_multiple_asids():
    practice = build_practice_metadata(asids=["123", "456"], ods_code="ABC")
    organisation_lookup = OrganisationLookup(practices=[practice], ccgs=[])

    expected = "ABC"

    actual = organisation_lookup.ods_code_from_asid("456")

    assert actual == expected


def test_ods_code_from_asid_returns_matching_practice_given_multiple_practices():
    practice_one = build_practice_metadata(asids=["123"])
    practice_two = build_practice_metadata(asids=["456"], ods_code="ABC")
    organisation_lookup = OrganisationLookup(practices=[practice_one, practice_two], ccgs=[])

    expected = "ABC"

    actual = organisation_lookup.ods_code_from_asid("456")

    assert actual == expected


def test_ccg_ods_code_from_practice_ods_code_returns_ccg_ods_code():
    practice = build_practice_metadata(ods_code="15D")
    ccg = build_ccg_metadata(ods_code="12C", practices=["15D"])
    organisation_lookup = OrganisationLookup(practices=[practice], ccgs=[ccg])

    expected = "12C"

    actual = organisation_lookup.ccg_ods_code_from_practice_ods_code("15D")

    assert actual == expected


def test_ccg_ods_code_from_practice_ods_code_returns_none_given_no_ccgs():
    organisation_lookup = OrganisationLookup(practices=[], ccgs=[])

    expected = None

    actual = organisation_lookup.ccg_ods_code_from_practice_ods_code("A123")

    assert actual == expected


def test_ccg_ods_code_from_practice_ods_code_returns_matching_ccg_with_multiple_practices():
    ccg = build_ccg_metadata(practices=["B3432", a_string(), a_string()], ods_code="3W")
    organisation_lookup = OrganisationLookup(practices=[], ccgs=[ccg])

    expected = "3W"

    actual = organisation_lookup.ccg_ods_code_from_practice_ods_code("B3432")

    assert actual == expected


def test_ccg_ods_code_from_practice_ods_code_returns_matching_ccg_given_multiple_ccgs():
    ccg = build_ccg_metadata(practices=["A2431"], ods_code="42C")
    organisation_lookup = OrganisationLookup(
        practices=[], ccgs=[build_ccg_metadata(), build_ccg_metadata(), ccg]
    )

    expected = "42C"

    actual = organisation_lookup.ccg_ods_code_from_practice_ods_code("A2431")

    assert actual == expected


def test_ccg_name_from_practice_ods_code_returns_ccg_name():
    practice = build_practice_metadata(ods_code="15D")
    ccg = build_ccg_metadata(name="Test CCG name", practices=["15D"])
    organisation_lookup = OrganisationLookup(practices=[practice], ccgs=[ccg])

    expected = "Test CCG name"

    actual = organisation_lookup.ccg_name_from_practice_ods_code("15D")

    assert actual == expected
