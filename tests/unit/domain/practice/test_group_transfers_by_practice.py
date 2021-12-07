from unittest.mock import Mock

from prmcalculator.domain.gp2gp.transfer import Practice
from prmcalculator.domain.ods_portal.organisation_metadata import PracticeDetails
from prmcalculator.domain.practice.group_transfers_by_practice import (
    PracticeTransfers,
    group_transfers_by_practice,
)
from prmcalculator.domain.practice.practice_lookup import PracticeLookup
from tests.builders.common import a_string
from tests.builders.gp2gp import build_transfer


def test_produces_empty_metrics_given_practices_with_no_transfers():
    mock_probe = Mock()
    lookup = PracticeLookup(
        [
            PracticeDetails(asids=[a_string()], ods_code="A1234", name="Practice 1"),
            PracticeDetails(asids=[a_string()], ods_code="B5678", name="Practice 2"),
        ]
    )

    expected = [
        PracticeTransfers(name="Practice 1", ods_code="A1234", transfers=()),
        PracticeTransfers(name="Practice 2", ods_code="B5678", transfers=()),
    ]

    actual = group_transfers_by_practice(
        transfers=[], practice_lookup=lookup, observability_probe=mock_probe
    )
    assert set(actual) == set(expected)


def test_produces_an_empty_metrics_object_given_practice_with_no_matching_transfers():
    mock_probe = Mock()
    ods_code = "A1234"
    lookup = PracticeLookup(
        [
            PracticeDetails(
                asids=["121212121212", "343434343434"], ods_code=ods_code, name="Test Practice"
            )
        ]
    )
    transfer = build_transfer(
        requesting_practice=Practice(asid="565656565656", supplier=a_string(12)),
    )

    actual = group_transfers_by_practice(
        transfers=[transfer], practice_lookup=lookup, observability_probe=mock_probe
    )

    expected = [PracticeTransfers(name="Test Practice", ods_code="A1234", transfers=())]

    assert actual == expected


def test_produces_a_group_given_single_practice_with_transfers_matching_asid():
    mock_probe = Mock()
    ods_code = "A1234"

    lookup = PracticeLookup(
        [PracticeDetails(asids=["121212121212"], ods_code=ods_code, name="Test Practice")]
    )
    transfer_one = build_transfer(
        requesting_practice=Practice(asid="121212121212", supplier=a_string(12)),
    )
    transfer_two = build_transfer(
        requesting_practice=Practice(asid="121212121212", supplier=a_string(12)),
    )

    expected = [
        PracticeTransfers(
            name="Test Practice", ods_code="A1234", transfers=(transfer_one, transfer_two)
        )
    ]

    actual = group_transfers_by_practice(
        transfers=[transfer_one, transfer_two],
        practice_lookup=lookup,
        observability_probe=mock_probe,
    )

    assert actual == expected


def test_produces_a_group_given_single_practice_with_transfers_matching_asids():
    mock_probe = Mock()
    ods_code = "A1234"
    lookup = PracticeLookup(
        [
            PracticeDetails(
                asids=["121212121212", "343434343434"], ods_code=ods_code, name="Test Practice"
            )
        ]
    )

    transfer_one = build_transfer(
        requesting_practice=Practice(asid="343434343434", supplier=a_string(12)),
    )

    transfer_two = build_transfer(
        requesting_practice=Practice(asid="121212121212", supplier=a_string(12)),
    )

    expected = [
        PracticeTransfers(
            name="Test Practice", ods_code="A1234", transfers=(transfer_one, transfer_two)
        )
    ]

    actual = group_transfers_by_practice(
        transfers=[transfer_one, transfer_two],
        practice_lookup=lookup,
        observability_probe=mock_probe,
    )

    assert actual == expected


def test_produces_correct_groups_given_two_practices_each_with_transfers():
    mock_probe = Mock()
    practice_a_ods_code = "A1234"
    practice_a_asid = "121212121212"
    practice_b_ods_code = "B4567"
    practice_b_asid = "3512352431233"
    lookup = PracticeLookup(
        [
            PracticeDetails(
                asids=[practice_a_asid], ods_code=practice_a_ods_code, name="Practice A"
            ),
            PracticeDetails(
                asids=[practice_b_asid], ods_code=practice_b_ods_code, name="Practice B"
            ),
        ]
    )
    practice_a_transfer = build_transfer(
        requesting_practice=Practice(asid=practice_a_asid, supplier=a_string(12)),
    )
    practice_b_transfer = build_transfer(
        requesting_practice=Practice(asid=practice_b_asid, supplier=a_string(12)),
    )

    expected = [
        PracticeTransfers(
            name="Practice A", ods_code=practice_a_ods_code, transfers=(practice_a_transfer,)
        ),
        PracticeTransfers(
            name="Practice B", ods_code=practice_b_ods_code, transfers=(practice_b_transfer,)
        ),
    ]

    actual = group_transfers_by_practice(
        transfers=[practice_a_transfer, practice_b_transfer],
        practice_lookup=lookup,
        observability_probe=mock_probe,
    )

    assert set(actual) == set(expected)


def test_calls_observability_probe_when_multiple_unknown_practices_for_transfers():
    mock_probe = Mock()

    lookup = PracticeLookup([])
    unknown_practice_transfer = build_transfer(
        requesting_practice=Practice(asid="121212121212", supplier=a_string(12))
    )

    group_transfers_by_practice(
        transfers=[unknown_practice_transfer],
        practice_lookup=lookup,
        observability_probe=mock_probe,
    )

    mock_probe.record_unknown_practice_for_transfer.assert_called_once_with(
        unknown_practice_transfer
    )
