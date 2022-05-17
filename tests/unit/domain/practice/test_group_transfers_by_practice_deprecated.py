from unittest.mock import Mock

from prmcalculator.domain.ods_portal.organisation_lookup import OrganisationLookup
from prmcalculator.domain.ods_portal.organisation_metadata import PracticeMetadata
from prmcalculator.domain.practice.group_transfers_by_practice_deprecated import (
    PracticeTransfersDeprecated,
    group_transfers_by_practice_deprecated,
)
from tests.builders.common import a_string
from tests.builders.gp2gp import build_practice_details, build_transfer


def test_produces_empty_metrics_given_practices_with_no_transfers():
    mock_probe = Mock()
    lookup = OrganisationLookup(
        practices=[
            PracticeMetadata(asids=[a_string()], ods_code="A1234", name="Practice 1"),
            PracticeMetadata(asids=[a_string()], ods_code="B5678", name="Practice 2"),
        ],
        ccgs=[],
    )

    expected = [
        PracticeTransfersDeprecated(
            name="Practice 1", ods_code="A1234", transfers=(), ccg_name=None, ccg_ods_code=None
        ),
        PracticeTransfersDeprecated(
            name="Practice 2", ods_code="B5678", transfers=(), ccg_name=None, ccg_ods_code=None
        ),
    ]

    actual = group_transfers_by_practice_deprecated(
        transfers=[], organisation_lookup=lookup, observability_probe=mock_probe
    )
    assert set(actual) == set(expected)


def test_produces_an_empty_metrics_object_given_practice_with_no_matching_transfers():
    mock_probe = Mock()
    ods_code = "A1234"
    lookup = OrganisationLookup(
        practices=[
            PracticeMetadata(
                asids=["121212121212", "343434343434"], ods_code=ods_code, name="Test Practice"
            )
        ],
        ccgs=[],
    )
    transfer = build_transfer(
        requesting_practice=build_practice_details(asid="565656565656"),
    )

    actual = group_transfers_by_practice_deprecated(
        transfers=[transfer], organisation_lookup=lookup, observability_probe=mock_probe
    )

    expected = [
        PracticeTransfersDeprecated(
            name="Test Practice", ods_code="A1234", transfers=(), ccg_name=None, ccg_ods_code=None
        )
    ]

    assert actual == expected


def test_produces_a_group_given_single_practice_with_transfers_matching_asid():
    mock_probe = Mock()
    ods_code = "A1234"

    lookup = OrganisationLookup(
        practices=[
            PracticeMetadata(asids=["121212121212"], ods_code=ods_code, name="Test Practice")
        ],
        ccgs=[],
    )
    transfer_one = build_transfer(
        requesting_practice=build_practice_details(asid="121212121212"),
    )
    transfer_two = build_transfer(
        requesting_practice=build_practice_details(asid="121212121212"),
    )

    expected = [
        PracticeTransfersDeprecated(
            name="Test Practice",
            ods_code="A1234",
            transfers=(transfer_one, transfer_two),
            ccg_name=None,
            ccg_ods_code=None,
        )
    ]

    actual = group_transfers_by_practice_deprecated(
        transfers=[transfer_one, transfer_two],
        organisation_lookup=lookup,
        observability_probe=mock_probe,
    )

    assert actual == expected


def test_produces_a_group_given_single_practice_with_transfers_matching_asids():
    mock_probe = Mock()
    ods_code = "A1234"
    lookup = OrganisationLookup(
        practices=[
            PracticeMetadata(
                asids=["121212121212", "343434343434"], ods_code=ods_code, name="Test Practice"
            )
        ],
        ccgs=[],
    )

    transfer_one = build_transfer(
        requesting_practice=build_practice_details(asid="343434343434"),
    )

    transfer_two = build_transfer(
        requesting_practice=build_practice_details(asid="121212121212"),
    )

    expected = [
        PracticeTransfersDeprecated(
            name="Test Practice",
            ods_code="A1234",
            transfers=(transfer_one, transfer_two),
            ccg_name=None,
            ccg_ods_code=None,
        )
    ]

    actual = group_transfers_by_practice_deprecated(
        transfers=[transfer_one, transfer_two],
        organisation_lookup=lookup,
        observability_probe=mock_probe,
    )

    assert actual == expected


def test_produces_correct_groups_given_two_practices_each_with_transfers():
    mock_probe = Mock()
    practice_a_ods_code = "A1234"
    practice_a_asid = "121212121212"
    practice_b_ods_code = "B4567"
    practice_b_asid = "3512352431233"
    lookup = OrganisationLookup(
        practices=[
            PracticeMetadata(
                asids=[practice_a_asid], ods_code=practice_a_ods_code, name="Practice A"
            ),
            PracticeMetadata(
                asids=[practice_b_asid], ods_code=practice_b_ods_code, name="Practice B"
            ),
        ],
        ccgs=[],
    )
    practice_a_transfer = build_transfer(
        requesting_practice=build_practice_details(asid=practice_a_asid),
    )
    practice_b_transfer = build_transfer(
        requesting_practice=build_practice_details(asid=practice_b_asid),
    )

    expected = [
        PracticeTransfersDeprecated(
            name="Practice A",
            ods_code=practice_a_ods_code,
            transfers=(practice_a_transfer,),
            ccg_name=None,
            ccg_ods_code=None,
        ),
        PracticeTransfersDeprecated(
            name="Practice B",
            ods_code=practice_b_ods_code,
            transfers=(practice_b_transfer,),
            ccg_name=None,
            ccg_ods_code=None,
        ),
    ]

    actual = group_transfers_by_practice_deprecated(
        transfers=[practice_a_transfer, practice_b_transfer],
        organisation_lookup=lookup,
        observability_probe=mock_probe,
    )

    assert set(actual) == set(expected)


def test_calls_observability_probe_when_multiple_unknown_practices_for_transfers():
    mock_probe = Mock()

    lookup = OrganisationLookup(practices=[], ccgs=[])
    unknown_practice_transfer = build_transfer(
        requesting_practice=build_practice_details(asid="121212121212")
    )

    group_transfers_by_practice_deprecated(
        transfers=[unknown_practice_transfer],
        organisation_lookup=lookup,
        observability_probe=mock_probe,
    )

    mock_probe.record_unknown_practice_for_transfer.assert_called_once_with(
        unknown_practice_transfer
    )
