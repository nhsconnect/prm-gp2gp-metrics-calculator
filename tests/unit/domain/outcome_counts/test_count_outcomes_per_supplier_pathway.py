import polars as pl
import pytest

from prmcalculator.domain.gp2gp.transfer import TransferStatus, TransferFailureReason
from prmcalculator.domain.outcome_counts.count_outcomes_per_supplier_pathway import (
    count_outcomes_per_supplier_pathway,
)
from tests.builders.common import a_string
from tests.builders.outcome_counts import TransferDataFrame


@pytest.mark.filterwarnings("ignore:Conversion of")
def test_returns_dataframe_with_supplier_and_transfer_outcome_columns():
    requesting_supplier = a_string(6)
    sending_supplier = a_string(6)
    status = TransferStatus.TECHNICAL_FAILURE.value
    failure_reason = TransferFailureReason.FINAL_ERROR.value
    df = (
        TransferDataFrame()
        .with_row(
            requesting_supplier=requesting_supplier,
            sending_supplier=sending_supplier,
            status=status,
            failure_reason=failure_reason,
        )
        .build()
    )

    actual_dataframe = count_outcomes_per_supplier_pathway(df)
    actual = actual_dataframe[
        ["requesting_supplier", "sending_supplier", "status", "failure_reason"]
    ]

    expected = pl.from_dict(
        {
            "requesting_supplier": [requesting_supplier],
            "sending_supplier": [sending_supplier],
            "status": [status],
            "failure_reason": [failure_reason],
        }
    )

    assert actual.frame_equal(expected, null_equal=True)


@pytest.mark.filterwarnings("ignore:Conversion of")
@pytest.mark.parametrize(
    "error_codes, expected",
    [
        ([4, 5, 3, 4, 4], "3,4,5"),
        ([4, 5, 5, 3, 4, 4, 5], "3,4,5"),
        ([None, None, 5], "5"),
        ([None], ""),
        ([], ""),
    ],
)
def test_returns_dataframe_with_unique_final_error_codes(error_codes, expected):
    df = TransferDataFrame().with_row(final_error_codes=error_codes).build()

    actual = count_outcomes_per_supplier_pathway(df)
    expected_unique_final_errors = pl.Series("unique_final_errors", [expected])

    assert actual["unique_final_errors"].series_equal(expected_unique_final_errors, null_equal=True)


@pytest.mark.filterwarnings("ignore:Conversion of")
@pytest.mark.parametrize(
    "error_codes, expected",
    [
        ([4, 5, 3, 4, 4], "3,4,5"),
        ([4, 5, 5, 3, 4, 4, 5], "3,4,5"),
        ([None, None, 5], "5"),
        ([None], ""),
        ([], ""),
    ],
)
def test_returns_dataframe_with_unique_sender_error_codes(error_codes, expected):
    df = TransferDataFrame().with_row(sender_error_codes=error_codes).build()

    actual = count_outcomes_per_supplier_pathway(df)
    expected_unique_sender_errors = pl.Series("unique_sender_errors", [expected])

    assert actual["unique_sender_errors"].series_equal(
        expected_unique_sender_errors, null_equal=True
    )


@pytest.mark.filterwarnings("ignore:Conversion of")
@pytest.mark.parametrize(
    "error_codes, expected",
    [
        ([4, 5, 3, 4, 4], "3,4,5"),
        ([4, 5, 5, 3, 4, 4, 5], "3,4,5"),
        ([], ""),
    ],
)
def test_returns_dataframe_with_unique_intermediate_error_codes(error_codes, expected):
    df = TransferDataFrame().with_row(intermediate_error_codes=error_codes).build()

    actual = count_outcomes_per_supplier_pathway(df)
    expected_unique_intermediate_errors = pl.Series("unique_intermediate_errors", [expected])

    assert actual["unique_intermediate_errors"].series_equal(
        expected_unique_intermediate_errors, null_equal=True
    )


@pytest.mark.filterwarnings("ignore:Conversion of")
def test_returns_sorted_count_per_supplier_pathway():
    supplier_a = a_string(6)
    supplier_b = a_string(6)
    df = (
        TransferDataFrame()
        .with_row(
            requesting_supplier=supplier_b,
            sending_supplier=supplier_a,
        )
        .with_row(
            requesting_supplier=supplier_a,
            sending_supplier=supplier_b,
        )
        .with_row(
            requesting_supplier=supplier_a,
            sending_supplier=supplier_b,
        )
        .build()
    )

    actual_dataframe = count_outcomes_per_supplier_pathway(df)
    actual = actual_dataframe[["requesting_supplier", "sending_supplier", "count"]]
    expected = pl.from_dict(
        {
            "requesting_supplier": [supplier_a, supplier_b],
            "sending_supplier": [supplier_b, supplier_a],
            "count": [2, 1],
        }
    )
    assert actual.frame_equal(expected, null_equal=True)


@pytest.mark.filterwarnings("ignore:Conversion of")
def test_returns_sorted_count_per_transfer_outcome():
    integrated_status = TransferStatus.INTEGRATED_ON_TIME.value
    integrated_failure_reason = None
    failed_status = TransferStatus.TECHNICAL_FAILURE.value
    failed_failure_reason = TransferFailureReason.FINAL_ERROR.value
    df = (
        TransferDataFrame()
        .with_row(status=integrated_status, failure_reason=integrated_failure_reason)
        .with_row(status=integrated_status, failure_reason=integrated_failure_reason)
        .with_row(status=failed_status, failure_reason=failed_failure_reason)
        .build()
    )

    actual_dataframe = count_outcomes_per_supplier_pathway(df)
    actual = actual_dataframe[["status", "failure_reason", "count"]]

    expected = pl.from_dict(
        {
            "status": [integrated_status, failed_status],
            "failure_reason": [integrated_failure_reason, failed_failure_reason],
            "count": [2, 1],
        }
    )
    assert actual.frame_equal(expected, null_equal=True)


@pytest.mark.filterwarnings("ignore:Conversion of")
@pytest.mark.parametrize(
    "error_codes_field_name, unique_error_codes_field_name, scenario_a_error_codes, \
     scenario_a_unique_errors, scenario_b_error_codes, scenario_b_unique_errors",
    [
        ("sender_error_codes", "unique_sender_errors", [15], "15", [], ""),
        ("sender_error_codes", "unique_sender_errors", [5, 3, 15, 5], "3,5,15", [43, 43], "43"),
        ("sender_error_codes", "unique_sender_errors", [5], "5", [None], ""),
        ("intermediate_error_codes", "unique_intermediate_errors", [23], "23", [], ""),
        (
            "intermediate_error_codes",
            "unique_intermediate_errors",
            [1, 4, 30, 1],
            "1,4,30",
            [34, 34],
            "34",
        ),
        ("final_error_codes", "unique_final_errors", [23], "23", [], ""),
        ("final_error_codes", "unique_final_errors", [6, 9, 10, 6], "6,9,10", [10, 10], "10"),
        ("final_error_codes", "unique_final_errors", [1], "1", [None], ""),
    ],
)
def test_returns_sorted_count_per_unique_error_combinations(
    error_codes_field_name,
    unique_error_codes_field_name,
    scenario_a_error_codes,
    scenario_a_unique_errors,
    scenario_b_error_codes,
    scenario_b_unique_errors,
):

    df = (
        TransferDataFrame()
        .with_row(**{error_codes_field_name: scenario_a_error_codes})
        .with_row(**{error_codes_field_name: scenario_a_error_codes})
        .with_row(**{error_codes_field_name: scenario_b_error_codes})
        .build()
    )

    actual_dataframe = count_outcomes_per_supplier_pathway(df)
    actual = actual_dataframe[[unique_error_codes_field_name, "count"]]

    expected = pl.from_dict(
        {
            unique_error_codes_field_name: [
                scenario_a_unique_errors,
                scenario_b_unique_errors,
            ],
            "count": [2, 1],
        }
    )
    assert actual.frame_equal(expected, null_equal=True)
