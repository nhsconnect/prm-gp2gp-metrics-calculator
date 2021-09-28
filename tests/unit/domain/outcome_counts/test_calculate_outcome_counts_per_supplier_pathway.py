import polars as pl

from prmcalculator.domain.gp2gp.transfer import TransferStatus, TransferFailureReason
from prmcalculator.domain.outcome_counts.calculate_outcome_counts_per_supplier_pathway import (
    calculate_outcome_counts_per_supplier_pathway,
)
from tests.builders.common import a_string
from tests.builders.outcome_counts import build_transfer_dataframe


def test_returns_dataframe_with_select_columns():
    requesting_supplier = a_string(6)
    sending_supplier = a_string(6)
    status = TransferStatus.TECHNICAL_FAILURE.value
    failure_reason = TransferFailureReason.FINAL_ERROR.value
    df = build_transfer_dataframe(
        requesting_supplier=requesting_supplier,
        sending_supplier=sending_supplier,
        status=status,
        failure_reason=failure_reason,
    )

    actual = calculate_outcome_counts_per_supplier_pathway(df)
    expected = pl.from_dict(
        {
            "requesting_supplier": [requesting_supplier],
            "sending_supplier": [sending_supplier],
            "status": [status],
            "failure_reason": [failure_reason],
        }
    )
    assert actual.frame_equal(expected, null_equal=True)
