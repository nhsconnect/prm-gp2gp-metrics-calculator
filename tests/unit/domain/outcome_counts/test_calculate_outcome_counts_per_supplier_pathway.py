import polars as pl
import pytest

from prmcalculator.domain.gp2gp.transfer import TransferStatus, TransferFailureReason
from prmcalculator.domain.outcome_counts.calculate_outcome_counts_per_supplier_pathway import (
    calculate_outcome_counts_per_supplier_pathway,
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

    actual_dataframe = calculate_outcome_counts_per_supplier_pathway(df)
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

    actual = calculate_outcome_counts_per_supplier_pathway(df)
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

    actual = calculate_outcome_counts_per_supplier_pathway(df)
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

    actual = calculate_outcome_counts_per_supplier_pathway(df)
    expected_unique_intermediate_errors = pl.Series("unique_intermediate_errors", [expected])

    assert actual["unique_intermediate_errors"].series_equal(
        expected_unique_intermediate_errors, null_equal=True
    )
