from unittest.mock import Mock

from prmcalculator.domain.practice.group_transfers_by_ccg import CCG, group_transfers_by_ccg
from tests.builders.gp2gp import build_practice


def test_produces_empty_list_given_no_practices():
    mock_probe = Mock()

    expected = []  # type: ignore

    actual = group_transfers_by_ccg(practices=[], observability_probe=mock_probe)
    assert actual == expected


def test_produces_a_ccg_group_given_single_practice():
    mock_probe = Mock()
    practice_ods_code = "A1234"
    practice_one = build_practice(
        ods_code=practice_ods_code, ccg_name="CCG 1", ccg_ods_code="AA1234"
    )

    expected = [
        CCG(
            ccg_name="CCG 1",
            ccg_ods_code="AA1234",
            practices_ods_codes=[practice_ods_code],
        )
    ]

    actual = group_transfers_by_ccg(
        practices=[practice_one],
        observability_probe=mock_probe,
    )

    assert actual == expected


def test_produces_multiple_ccg_groups_given_a_multiple_practices():
    mock_probe = Mock()
    practice_one_ods_code = "A1234"
    practice_two_ods_code = "A2345"
    practice_three_ods_code = "B1234"
    practice_one = build_practice(
        name="Practice 1", ods_code=practice_one_ods_code, ccg_name="CCG 1", ccg_ods_code="AA1234"
    )

    practice_two = build_practice(
        name="Practice 2", ods_code=practice_two_ods_code, ccg_name="CCG 1", ccg_ods_code="AA1234"
    )

    practice_three = build_practice(
        name="Practice 3", ods_code=practice_three_ods_code, ccg_name="CCG 2", ccg_ods_code="BB1234"
    )

    expected = [
        CCG(
            ccg_name="CCG 1",
            ccg_ods_code="AA1234",
            practices_ods_codes=[practice_one_ods_code, practice_two_ods_code],
        ),
        CCG(
            ccg_name="CCG 2",
            ccg_ods_code="BB1234",
            practices_ods_codes=[practice_three_ods_code],
        ),
    ]

    actual = group_transfers_by_ccg(
        practices=[practice_one, practice_two, practice_three],
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
