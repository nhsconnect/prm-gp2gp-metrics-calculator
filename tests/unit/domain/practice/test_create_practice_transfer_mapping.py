from prmcalculator.domain.gp2gp.transfer import Practice
from prmcalculator.domain.ods_portal.organisation_metadata import PracticeDetails
from prmcalculator.domain.practice.create_practice_transfer_mapping import (
    create_practice_transfer_mapping,
)
from prmcalculator.domain.practice.practice_lookup import PracticeLookup
from tests.builders.common import a_string
from tests.builders.gp2gp import build_transfer


def test_returns_dict_that_maps_ods_code_to_transfers():
    ods_code = "A1234"
    lookup = PracticeLookup(
        [
            PracticeDetails(
                asids=["121212121212", "343434343434"], ods_code=ods_code, name=a_string()
            )
        ]
    )
    transfers = [
        build_transfer(
            requesting_practice=Practice(asid="343434343434", supplier=a_string(12)),
        ),
        build_transfer(
            requesting_practice=Practice(asid="121212121212", supplier=a_string(12)),
        ),
    ]

    actual_practice_transfers = create_practice_transfer_mapping(
        transfers=transfers, practice_lookup=lookup
    )

    assert actual_practice_transfers[ods_code] == transfers
    assert len(actual_practice_transfers.keys()) == 1


def test_returns_an_empty_list_for_practice_with_no_transfers():
    ods_code = "A1234"
    lookup = PracticeLookup(
        [
            PracticeDetails(
                asids=["121212121212", "343434343434"], ods_code=ods_code, name=a_string()
            )
        ]
    )
    transfers = [build_transfer()]

    practice_transfers = create_practice_transfer_mapping(
        transfers=transfers, practice_lookup=lookup
    )

    actual = practice_transfers[ods_code]

    assert actual == []


def test_returns_dict_that_maps_multiple_ods_code_to_transfers():
    practice_a_ods_code = "A1234"
    practice_a_asid = "121212121212"
    practice_b_ods_code = "B4567"
    practice_b_asid = "3512352431233"
    lookup = PracticeLookup(
        [
            PracticeDetails(asids=[practice_a_asid], ods_code=practice_a_ods_code, name=a_string()),
            PracticeDetails(asids=[practice_b_asid], ods_code=practice_b_ods_code, name=a_string()),
        ]
    )
    practice_a_transfer = build_transfer(
        requesting_practice=Practice(asid=practice_a_asid, supplier=a_string(12)),
    )
    practice_b_transfer = build_transfer(
        requesting_practice=Practice(asid=practice_b_asid, supplier=a_string(12)),
    )

    practice_transfers = create_practice_transfer_mapping(
        transfers=[practice_a_transfer, practice_b_transfer], practice_lookup=lookup
    )

    actual = practice_transfers

    assert actual[practice_a_ods_code] == [practice_a_transfer]
    assert actual[practice_b_ods_code] == [practice_b_transfer]
    assert len(actual.keys()) == 2
