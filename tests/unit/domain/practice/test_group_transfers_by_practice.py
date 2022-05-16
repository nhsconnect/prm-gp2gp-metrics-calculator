from unittest.mock import Mock

from prmcalculator.domain.practice.group_transfers_by_practice import (
    Practice,
    group_transfers_by_practice,
)
from tests.builders.gp2gp import build_practice, build_transfer


def test_produces_empty_metrics_given_practices_with_no_transfers():
    mock_probe = Mock()

    expected = []  # type: ignore

    actual = group_transfers_by_practice(transfers=[], observability_probe=mock_probe)
    assert actual == expected


def test_produces_a_group_given_single_practice_with_a_single_transfer():
    mock_probe = Mock()

    transfer_one = build_transfer(
        requesting_practice=build_practice(
            ods_code="A1234", name="Practice 1", ccg_name="CCG 1", ccg_ods_code="AA1234"
        )
    )

    expected = [
        Practice(
            name="Practice 1",
            ods_code="A1234",
            transfers=[transfer_one],
            ccg_name="CCG 1",
            ccg_ods_code="AA1234",
        )
    ]

    actual = group_transfers_by_practice(
        transfers=[transfer_one],
        observability_probe=mock_probe,
    )

    assert actual == expected


def test_produces_a_group_given_single_practice_with_multiple_transfer():
    mock_probe = Mock()

    transfer_one = build_transfer(
        requesting_practice=build_practice(
            ods_code="A1234", name="Practice 1", ccg_name="CCG 1", ccg_ods_code="AA1234"
        ),
    )
    transfer_two = build_transfer(
        requesting_practice=build_practice(
            ods_code="A1234", name="Practice 1", ccg_name="CCG 1", ccg_ods_code="AA1234"
        ),
    )

    expected = [
        Practice(
            name="Practice 1",
            ods_code="A1234",
            transfers=[transfer_one, transfer_two],
            ccg_name="CCG 1",
            ccg_ods_code="AA1234",
        )
    ]

    actual = group_transfers_by_practice(
        transfers=[transfer_one, transfer_two],
        observability_probe=mock_probe,
    )

    assert actual == expected


def test_produces_correct_groups_given_two_practices_each_with_transfers():
    mock_probe = Mock()

    transfer_one = build_transfer(
        requesting_practice=build_practice(
            ods_code="A1234", name="Practice 1", ccg_name="CCG 1", ccg_ods_code="AA1234"
        ),
    )
    transfer_two = build_transfer(
        requesting_practice=build_practice(
            ods_code="B1234", name="Practice 2", ccg_name="CCG 2", ccg_ods_code="BB1234"
        ),
    )
    transfer_three = build_transfer(
        requesting_practice=build_practice(
            ods_code="B1234", name="Practice 3", ccg_name="CCG 2", ccg_ods_code="BB1234"
        ),
    )

    expected = [
        Practice(
            name="Practice 1",
            ods_code="A1234",
            transfers=[transfer_one],
            ccg_name="CCG 1",
            ccg_ods_code="AA1234",
        ),
        Practice(
            name="Practice 2",
            ods_code="B1234",
            transfers=[transfer_two, transfer_three],
            ccg_name="CCG 2",
            ccg_ods_code="BB1234",
        ),
    ]

    actual = group_transfers_by_practice(
        transfers=[transfer_one, transfer_two, transfer_three],
        observability_probe=mock_probe,
    )

    assert actual == expected


#
# def test_calls_observability_probe_when_multiple_unknown_practices_for_transfers():
#     mock_probe = Mock()
#
#     lookup = OrganisationLookup(practices=[], ccgs=[])
#     unknown_practice_transfer = build_transfer(
#         requesting_practice=build_practice(asid="121212121212")
#     )
#
#     group_transfers_by_practice_deprecated(
#         transfers=[unknown_practice_transfer],
#         organisation_lookup=lookup,
#         observability_probe=mock_probe,
#     )
#
#     mock_probe.record_unknown_practice_for_transfer.assert_called_once_with(
#         unknown_practice_transfer
#     )
