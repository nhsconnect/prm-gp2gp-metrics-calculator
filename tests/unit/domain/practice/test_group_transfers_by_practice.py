from unittest.mock import Mock

from prmcalculator.domain.gp2gp.transfer import Practice
from prmcalculator.domain.ods_portal.organisation_metadata import PracticeDetails
from prmcalculator.domain.practice.group_transfers_by_practice import (
    group_transfers_by_practice,
)
from prmcalculator.domain.practice.practice_lookup import PracticeLookup
from tests.builders.common import a_string, a_datetime
from tests.builders.gp2gp import (
    build_transfer,
    a_transfer_integrated_within_3_days,
    a_transfer_integrated_beyond_8_days,
)


def test_produces_empty_metrics_given_practices_with_no_transfers():
    mock_probe = Mock()
    lookup = PracticeLookup(
        [
            PracticeDetails(asids=[a_string()], ods_code="A1234", name="Practice 1"),
            PracticeDetails(asids=[a_string()], ods_code="B5678", name="Practice 2"),
        ]
    )

    expected_practices = {("A1234", "Practice 1"), ("B5678", "Practice 2")}

    actual = group_transfers_by_practice(
        transfers=[], practice_lookup=lookup, observability_probe=mock_probe
    )
    actual_practices = {(metrics.ods_code, metrics.name) for metrics in actual.values()}

    assert actual_practices == expected_practices


def test_produces_an_empty_metrics_object_given_practice_with_no_matching_transfers():
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
            date_requested=a_datetime(year=2020, month=1),
            requesting_practice=Practice(asid="565656565656", supplier=a_string(12)),
        )
    ]

    expected_requested = 0

    actual = group_transfers_by_practice(
        transfers=transfers, practice_lookup=lookup, observability_probe=mock_probe
    )
    actual_metrics = actual["A1234"].monthly_metrics(2020, 1)

    assert actual_metrics.requested_by_practice_total() == expected_requested


def test_produces_a_group_given_single_practice_with_transfers_matching_asid():
    mock_probe = Mock()
    ods_code = "A1234"

    lookup = PracticeLookup(
        [PracticeDetails(asids=["121212121212"], ods_code=ods_code, name=a_string())]
    )
    transfers = [
        build_transfer(
            date_requested=a_datetime(year=2020, month=1),
            requesting_practice=Practice(asid="121212121212", supplier=a_string(12)),
        ),
        build_transfer(
            date_requested=a_datetime(year=2020, month=1),
            requesting_practice=Practice(asid="121212121212", supplier=a_string(12)),
        ),
    ]

    expected_requested = 2

    actual = group_transfers_by_practice(
        transfers=transfers, practice_lookup=lookup, observability_probe=mock_probe
    )
    actual_metrics = actual["A1234"].monthly_metrics(2020, 1)

    assert actual_metrics.requested_by_practice_total() == expected_requested


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
            date_requested=a_datetime(year=2020, month=1),
            requesting_practice=Practice(asid="343434343434", supplier=a_string(12)),
        ),
        build_transfer(
            date_requested=a_datetime(year=2020, month=1),
            requesting_practice=Practice(asid="121212121212", supplier=a_string(12)),
        ),
    ]

    expected_requested = 2

    actual = group_transfers_by_practice(
        transfers=transfers, practice_lookup=lookup, observability_probe=mock_probe
    )
    actual_metrics = actual["A1234"].monthly_metrics(2020, 1)

    assert actual_metrics.requested_by_practice_total() == expected_requested


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
    practice_a_transfer = a_transfer_integrated_within_3_days(
        date_requested=a_datetime(year=2020, month=1),
        requesting_practice=Practice(asid=practice_a_asid, supplier=a_string(12)),
    )
    practice_b_transfer = a_transfer_integrated_beyond_8_days(
        date_requested=a_datetime(year=2020, month=1),
        requesting_practice=Practice(asid=practice_b_asid, supplier=a_string(12)),
    )

    transfers = [practice_a_transfer, practice_b_transfer]

    actual = group_transfers_by_practice(
        transfers=transfers, practice_lookup=lookup, observability_probe=mock_probe
    )

    actual_practice_a_metrics = actual[practice_a_ods_code].monthly_metrics(2020, 1)
    actual_practice_b_metrics = actual[practice_b_ods_code].monthly_metrics(2020, 1)

    assert actual_practice_a_metrics.integrated_within_3_days() == 1
    assert actual_practice_b_metrics.integrated_beyond_8_days() == 1
    assert len(actual.keys()) == 2


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
