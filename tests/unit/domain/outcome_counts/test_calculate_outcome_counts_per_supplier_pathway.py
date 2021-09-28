import polars as pl

from prmcalculator.domain.gp2gp.transfer import TransferStatus, TransferFailureReason
from prmcalculator.domain.outcome_counts.calculate_outcome_counts_per_supplier_pathway import (
    calculate_outcome_counts_per_supplier_pathway,
)
from tests.builders.common import a_string
from tests.builders.outcome_counts import TransferDataFrame


def test_returns_dataframe_with_select_columns():
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
            final_error_codes=[1],
        )
        .build()
    )

    actual = calculate_outcome_counts_per_supplier_pathway(df)
    expected = pl.from_dict(
        {
            "requesting_supplier": [requesting_supplier],
            "sending_supplier": [sending_supplier],
            "status": [status],
            "failure_reason": [failure_reason],
            "final_error_codes": [[1]],
            "unique_final_errors": ["1"],
        }
    )

    assert actual.frame_equal(expected, null_equal=True)


def test_returns_dataframe_with_unique_final_error_codes():
    df = TransferDataFrame().with_row(final_error_codes=[4, 5, 3, 4, 4]).build()

    actual = calculate_outcome_counts_per_supplier_pathway(df)
    expected_unique_final_errors = pl.Series("unique_final_errors", ["3,4,5"])

    assert actual["unique_final_errors"].series_equal(expected_unique_final_errors, null_equal=True)
