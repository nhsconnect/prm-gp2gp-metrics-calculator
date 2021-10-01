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
        ([7, 9, 6, 7, 7], "6 - Not at surgery, 7 - GP2GP disabled, 9 - Unexpected EHR"),
        ([7, 9, 9, 6, 7, 7, 9], "6 - Not at surgery, 7 - GP2GP disabled, 9 - Unexpected EHR"),
        ([None, None, 9], "9 - Unexpected EHR"),
        ([None], ""),
        ([], ""),
        ([1], "1 - Unknown error code"),
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
        ([7, 9, 6, 7, 7], "6 - Not at surgery, 7 - GP2GP disabled, 9 - Unexpected EHR"),
        ([7, 9, 9, 6, 7, 7, 9], "6 - Not at surgery, 7 - GP2GP disabled, 9 - Unexpected EHR"),
        ([None, None, 9], "9 - Unexpected EHR"),
        ([None], ""),
        ([], ""),
        ([1], "1 - Unknown error code"),
    ],
)
def test_returns_dataframe_with_unique_sender_errors(error_codes, expected):
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
        ([7, 9, 6, 7, 7], "6 - Not at surgery, 7 - GP2GP disabled, 9 - Unexpected EHR"),
        ([7, 9, 9, 6, 7, 7, 9], "6 - Not at surgery, 7 - GP2GP disabled, 9 - Unexpected EHR"),
        ([], ""),
        ([1], "1 - Unknown error code"),
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
        ("sender_error_codes", "unique_sender_errors", [15], "15 - ABA suppressed", [], ""),
        (
            "sender_error_codes",
            "unique_sender_errors",
            [7, 6, 15, 7],
            "6 - Not at surgery, 7 - GP2GP disabled, 15 - ABA suppressed",
            [99, 99],
            "99 - Unexpected",
        ),
        ("sender_error_codes", "unique_sender_errors", [10], "10 - Failed to generate", [None], ""),
        (
            "intermediate_error_codes",
            "unique_intermediate_errors",
            [13],
            "13 - Config issue",
            [],
            "",
        ),
        (
            "intermediate_error_codes",
            "unique_intermediate_errors",
            [9, 13, 24, 9],
            "9 - Unexpected EHR, 13 - Config issue, 24 - SDS lookup",
            [20, 20],
            "20 - Spine error",
        ),
        ("final_error_codes", "unique_final_errors", [23], "23 - Sender not LM compliant", [], ""),
        (
            "final_error_codes",
            "unique_final_errors",
            [6, 9, 10, 6],
            "6 - Not at surgery, 9 - Unexpected EHR, 10 - Failed to generate",
            [11, 11],
            "11 - Failed to integrate",
        ),
        ("final_error_codes", "unique_final_errors", [17], "17 - ABA wrong patient", [None], ""),
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


@pytest.mark.filterwarnings("ignore:Conversion of")
def test_returns_sorted_count_by_count_and_supplier_and_status_per_scenario():
    integrated_status = TransferStatus.INTEGRATED_ON_TIME.value
    failed_status = TransferStatus.TECHNICAL_FAILURE.value
    process_failure_status = TransferStatus.PROCESS_FAILURE.value
    supplier_a = "SupplierA"
    supplier_b = "SupplierB"

    df = (
        TransferDataFrame()
        .with_row(
            status=integrated_status, requesting_supplier=supplier_b, sending_supplier=supplier_a
        )
        .with_row(
            status=integrated_status, requesting_supplier=supplier_b, sending_supplier=supplier_a
        )
        .with_row(
            status=integrated_status, requesting_supplier=supplier_b, sending_supplier=supplier_a
        )
        .with_row(
            status=integrated_status, requesting_supplier=supplier_a, sending_supplier=supplier_b
        )
        .with_row(
            status=integrated_status, requesting_supplier=supplier_a, sending_supplier=supplier_b
        )
        .with_row(status=failed_status, requesting_supplier=supplier_b, sending_supplier=supplier_a)
        .with_row(
            status=failed_status,
            requesting_supplier=supplier_a,
            sending_supplier=supplier_b,
        )
        .with_row(
            status=process_failure_status,
            requesting_supplier=supplier_b,
            sending_supplier=supplier_a,
        )
        .build()
    )

    actual_dataframe = count_outcomes_per_supplier_pathway(df)
    actual = actual_dataframe[["status", "requesting_supplier", "sending_supplier", "count"]]
    expected = pl.from_dict(
        {
            "status": [
                integrated_status,
                integrated_status,
                failed_status,
                process_failure_status,
                failed_status,
            ],
            "requesting_supplier": [supplier_b, supplier_a, supplier_a, supplier_b, supplier_b],
            "sending_supplier": [supplier_a, supplier_b, supplier_b, supplier_a, supplier_a],
            "count": [3, 2, 1, 1, 1],
        }
    )
    assert actual.frame_equal(expected, null_equal=True)


@pytest.mark.filterwarnings("ignore:Conversion of")
def test_returns_dataframe_with_percentage_of_transfers_rounded_to_3_decimal_places():
    integrated_status = TransferStatus.INTEGRATED_ON_TIME.value
    failed_status = TransferStatus.TECHNICAL_FAILURE.value
    process_failure_status = TransferStatus.PROCESS_FAILURE.value

    df = (
        TransferDataFrame()
        .with_row(status=integrated_status)
        .with_row(status=integrated_status)
        .with_row(status=integrated_status)
        .with_row(status=integrated_status)
        .with_row(status=failed_status)
        .with_row(status=failed_status)
        .with_row(status=process_failure_status)
        .build()
    )

    actual_dataframe = count_outcomes_per_supplier_pathway(df)
    actual = actual_dataframe[["status", "%_of_transfers"]]

    expected = pl.from_dict(
        {
            "status": [integrated_status, failed_status, process_failure_status],
            "%_of_transfers": [57.143, 28.571, 14.286],
        }
    )
    assert actual.frame_equal(expected, null_equal=True)


@pytest.mark.filterwarnings("ignore:Conversion of")
def test_returns_dataframe_with_percentage_of_technical_failures_rounded_to_3_decimal_places():
    integrated_status = TransferStatus.INTEGRATED_ON_TIME.value
    failed_status = TransferStatus.TECHNICAL_FAILURE.value
    final_error_failure_reason = TransferFailureReason.FINAL_ERROR.value
    sender_error_failure_reason = TransferFailureReason.FATAL_SENDER_ERROR.value
    copc_not_sent_failure_reason = TransferFailureReason.COPC_NOT_SENT.value

    df = (
        TransferDataFrame()
        .with_row(status=integrated_status, failure_reason=None)
        .with_row(status=failed_status, failure_reason=final_error_failure_reason)
        .with_row(status=failed_status, failure_reason=final_error_failure_reason)
        .with_row(status=failed_status, failure_reason=final_error_failure_reason)
        .with_row(status=failed_status, failure_reason=final_error_failure_reason)
        .with_row(status=failed_status, failure_reason=sender_error_failure_reason)
        .with_row(status=failed_status, failure_reason=sender_error_failure_reason)
        .with_row(status=failed_status, failure_reason=copc_not_sent_failure_reason)
        .build()
    )

    actual_dataframe = count_outcomes_per_supplier_pathway(df)
    actual = actual_dataframe[["status", "failure_reason", "%_of_technical_failures"]]

    expected = pl.from_dict(
        {
            "status": [failed_status, failed_status, integrated_status, failed_status],
            "failure_reason": [
                final_error_failure_reason,
                sender_error_failure_reason,
                None,
                copc_not_sent_failure_reason,
            ],
            "%_of_technical_failures": [57.143, 28.571, None, 14.286],
        }
    )
    assert actual.frame_equal(expected, null_equal=True)


@pytest.mark.filterwarnings("ignore:Conversion of")
def test_returns_dataframe_with_percentage_of_supplier_pathway_rounded_to_3_decimal_places():
    supplier_a = "SupplierA"
    supplier_b = "SupplierB"
    integrated_status = TransferStatus.INTEGRATED_ON_TIME.value
    failed_status = TransferStatus.TECHNICAL_FAILURE.value
    process_failure_status = TransferStatus.PROCESS_FAILURE.value

    df = (
        TransferDataFrame()
        .with_row(
            requesting_supplier=supplier_a, sending_supplier=supplier_b, status=integrated_status
        )
        .with_row(
            requesting_supplier=supplier_a, sending_supplier=supplier_b, status=integrated_status
        )
        .with_row(
            requesting_supplier=supplier_a, sending_supplier=supplier_b, status=integrated_status
        )
        .with_row(
            requesting_supplier=supplier_a, sending_supplier=supplier_b, status=integrated_status
        )
        .with_row(requesting_supplier=supplier_a, sending_supplier=supplier_b, status=failed_status)
        .with_row(requesting_supplier=supplier_a, sending_supplier=supplier_b, status=failed_status)
        .with_row(
            requesting_supplier=supplier_a,
            sending_supplier=supplier_b,
            status=process_failure_status,
        )
        .with_row(
            requesting_supplier=supplier_b, sending_supplier=supplier_a, status=integrated_status
        )
        .with_row(
            requesting_supplier=supplier_a, sending_supplier=supplier_a, status=integrated_status
        )
        .with_row(
            requesting_supplier=supplier_a, sending_supplier=supplier_a, status=integrated_status
        )
        .build()
    )

    actual_dataframe = count_outcomes_per_supplier_pathway(df)
    actual = actual_dataframe[
        ["requesting_supplier", "sending_supplier", "status", "%_of_supplier_pathway"]
    ]

    expected = pl.from_dict(
        {
            "requesting_supplier": [supplier_a, supplier_a, supplier_a, supplier_a, supplier_b],
            "sending_supplier": [supplier_b, supplier_a, supplier_b, supplier_b, supplier_a],
            "status": [
                integrated_status,
                integrated_status,
                failed_status,
                process_failure_status,
                integrated_status,
            ],
            "%_of_supplier_pathway": [57.143, 100, 28.571, 14.286, 100],
        }
    )
    assert actual.frame_equal(expected, null_equal=True)
