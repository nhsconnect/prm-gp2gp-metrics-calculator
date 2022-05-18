from unittest.mock import Mock

from prmcalculator.domain.practice.transfer_service import Practice, TransfersService
from tests.builders.common import a_datetime, a_string
from tests.builders.gp2gp import build_practice_details, build_transfer


def test_produces_empty_list_given_no_transfers():
    mock_probe = Mock()

    expected = []  # type: ignore

    actual = TransfersService(
        transfers=[], observability_probe=mock_probe
    ).group_transfers_by_practice()
    assert actual == expected


def test_produces_a_group_given_a_single_practice_with_a_single_transfer():
    mock_probe = Mock()

    transfer_one = build_transfer(
        requesting_practice=build_practice_details(
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

    actual = TransfersService(
        transfers=[transfer_one], observability_probe=mock_probe
    ).group_transfers_by_practice()

    assert actual == expected


def test_produces_a_group_given_a_single_practice_with_multiple_transfer():
    mock_probe = Mock()

    transfer_one = build_transfer(
        requesting_practice=build_practice_details(
            ods_code="A1234", name="Practice 1", ccg_name="CCG 1", ccg_ods_code="AA1234"
        ),
    )
    transfer_two = build_transfer(
        requesting_practice=build_practice_details(
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

    actual = TransfersService(
        transfers=[transfer_one, transfer_two], observability_probe=mock_probe
    ).group_transfers_by_practice()

    assert actual == expected


def test_sets_practice_fields_based_on_latest_transfer_transfer():
    mock_probe = Mock()

    transfer_one_oldest = build_transfer(
        date_requested=a_datetime(year=2020, month=1, day=1),
        requesting_practice=build_practice_details(
            ods_code="A1234", name="Practice Older", ccg_name="CCG 1", ccg_ods_code="AA1234"
        ),
    )
    transfer_two_latest = build_transfer(
        date_requested=a_datetime(year=2020, month=1, day=30),
        requesting_practice=build_practice_details(
            ods_code="A1234",
            name="Practice Latest",
            ccg_name="CCG Latest",
            ccg_ods_code="LATEST1234",
        ),
    )
    transfer_three_old = build_transfer(
        date_requested=a_datetime(year=2020, month=1, day=5),
        requesting_practice=build_practice_details(
            ods_code="A1234", name="Practice Old", ccg_name="CCG 1", ccg_ods_code="AA1234"
        ),
    )

    expected = [
        Practice(
            name="Practice Latest",
            ods_code="A1234",
            transfers=[transfer_one_oldest, transfer_two_latest, transfer_three_old],
            ccg_name="CCG Latest",
            ccg_ods_code="LATEST1234",
        )
    ]

    actual = TransfersService(
        transfers=[transfer_one_oldest, transfer_two_latest, transfer_three_old],
        observability_probe=mock_probe,
    ).group_transfers_by_practice()

    assert actual == expected


def test_produces_correct_groups_given_two_practices_each_with_transfers():
    mock_probe = Mock()

    transfer_one = build_transfer(
        requesting_practice=build_practice_details(
            ods_code="A1234", name="Practice 1", ccg_name="CCG 1", ccg_ods_code="AA1234"
        ),
    )
    transfer_two = build_transfer(
        requesting_practice=build_practice_details(
            ods_code="B1234", name="Practice 2", ccg_name="CCG 2", ccg_ods_code="BB1234"
        ),
    )
    transfer_three = build_transfer(
        requesting_practice=build_practice_details(
            ods_code="B1234", name="Practice 2", ccg_name="CCG 2", ccg_ods_code="BB1234"
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

    actual = TransfersService(
        transfers=[transfer_one, transfer_two, transfer_three], observability_probe=mock_probe
    ).group_transfers_by_practice()

    assert actual == expected


def test_ignore_transfer_and_log_when_missing_practice_ods_code():
    mock_probe = Mock()

    transfer_missing_ods_code = build_transfer(
        requesting_practice=build_practice_details(
            ods_code=None, name="Practice 1", ccg_name="CCG 1", ccg_ods_code="AA1234"
        ),
    )

    expected = []  # type: ignore

    actual = TransfersService(
        transfers=[transfer_missing_ods_code], observability_probe=mock_probe
    ).group_transfers_by_practice()

    mock_probe.record_unknown_practice_ods_code_for_transfer.assert_called_once_with(
        transfer_missing_ods_code
    )

    assert actual == expected


def test_ignore_transfer_and_log_when_missing_ccg_ods_code():
    mock_probe = Mock()

    transfer_missing_ccg_ods_code = build_transfer(
        requesting_practice=build_practice_details(
            ods_code=a_string(6), name="Practice 1", ccg_name="CCG 1", ccg_ods_code=None
        ),
    )

    expected = []  # type: ignore

    actual = TransfersService(
        transfers=[transfer_missing_ccg_ods_code], observability_probe=mock_probe
    ).group_transfers_by_practice()

    mock_probe.record_unknown_practice_ccg_ods_code_for_transfer.assert_called_once_with(
        transfer_missing_ccg_ods_code
    )

    assert actual == expected
