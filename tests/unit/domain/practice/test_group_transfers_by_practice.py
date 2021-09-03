from unittest.mock import Mock

import pytest

from prmcalculator.domain.gp2gp.transfer import Practice
from prmcalculator.domain.ods_portal.organisation_metadata import PracticeDetails
from prmcalculator.domain.practice.group_transfers_by_practice import (
    group_transfers_by_practice,
)
from prmcalculator.domain.practice.practice_lookup import PracticeLookup
from tests.builders.common import a_string
from tests.builders.gp2gp import build_transfer


@pytest.mark.filterwarnings("ignore:Unexpected ASID count:RuntimeWarning")
def test_produces_an_empty_list_given_practice_with_no_matching_transfers():
    mock_probe = Mock()
    ods_code = "A1234"
    lookup = PracticeLookup(
        [
            PracticeDetails(
                asids=["121212121212", "343434343434"], ods_code=ods_code, name=a_string()
            )
        ]
    )
    transfers = [
        build_transfer(requesting_practice=Practice(asid="565656565656", supplier=a_string(12)))
    ]

    practice_transfers = group_transfers_by_practice(
        transfers=transfers, practice_lookup=lookup, observability_probe=mock_probe
    )

    actual = practice_transfers[ods_code]

    assert actual == []


def test_produces_a_group_given_single_practice_with_transfers_matching_asid():
    mock_probe = Mock()
    ods_code = "A1234"

    lookup = PracticeLookup(
        [PracticeDetails(asids=["121212121212"], ods_code=ods_code, name=a_string())]
    )
    transfers = [
        build_transfer(requesting_practice=Practice(asid="121212121212", supplier=a_string(12))),
        build_transfer(requesting_practice=Practice(asid="121212121212", supplier=a_string(12))),
    ]

    actual_practice_transfers = group_transfers_by_practice(
        transfers=transfers, practice_lookup=lookup, observability_probe=mock_probe
    )

    assert actual_practice_transfers[ods_code] == transfers
    assert len(actual_practice_transfers.keys()) == 1


def test_produces_a_group_given_single_practice_with_transfers_matching_asids():
    mock_probe = Mock()
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

    actual_practice_transfers = group_transfers_by_practice(
        transfers=transfers, practice_lookup=lookup, observability_probe=mock_probe
    )

    assert actual_practice_transfers[ods_code] == transfers
    assert len(actual_practice_transfers.keys()) == 1


def test_produces_correct_groups_given_two_practices_each_with_transfers():
    mock_probe = Mock()
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

    practice_transfers = group_transfers_by_practice(
        transfers=[practice_a_transfer, practice_b_transfer],
        practice_lookup=lookup,
        observability_probe=mock_probe,
    )

    actual = practice_transfers

    assert actual[practice_a_ods_code] == [practice_a_transfer]
    assert actual[practice_b_ods_code] == [practice_b_transfer]
    assert len(actual.keys()) == 2


def test_calls_observability_probe_when_unexpected_asid_count():
    mock_probe = Mock()
    unexpected_asids = {"121212121212", "343434343434"}
    lookup = PracticeLookup([])
    transfers = [
        build_transfer(requesting_practice=Practice(asid="121212121212", supplier=a_string(12))),
        build_transfer(requesting_practice=Practice(asid="343434343434", supplier=a_string(12))),
    ]

    group_transfers_by_practice(
        transfers=transfers, practice_lookup=lookup, observability_probe=mock_probe
    )

    mock_probe.unexpected_asid_count.assert_called_once_with(unexpected_asids)
