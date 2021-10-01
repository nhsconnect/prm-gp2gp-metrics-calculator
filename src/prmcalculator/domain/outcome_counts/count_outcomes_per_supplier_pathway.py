from typing import List, Optional, Union
import polars as pl
from polars import col, count, when  # type: ignore

from prmcalculator.domain.gp2gp.transfer import TransferStatus

default_error_description_mapping = {
    6: "Not at surgery",
    7: "GP2GP disabled",
    9: "Unexpected EHR",
    10: "Failed to generate",
    11: "Failed to integrate",
    12: "Duplicate EHR",
    13: "Config issue",
    14: "Req not LM compliant",
    15: "ABA suppressed",
    17: "ABA wrong patient",
    18: "Req malformed",
    19: "Unauthorised req",
    20: "Spine error",
    21: "Extract malformed",
    23: "Sender not LM compliant",
    24: "SDS lookup",
    25: "Timeout",
    26: "Filed as attachment",
    28: "Wrong patient",
    29: "LM reassembly",
    30: "LM general failure",
    31: "Missing LM",
    99: "Unexpected",
}


def _error_description(error_code: int) -> str:
    try:
        return default_error_description_mapping[error_code]
    except KeyError:
        return "Unknown error code"


def _unique_errors(errors: List[Optional[int]]):
    unique_error_codes = {error_code for error_code in errors if error_code is not None}
    return ", ".join([f"{e} - {_error_description(e)}" for e in sorted(unique_error_codes)])


def _calculate_percentage(count_column: pl.Series, total: int) -> Union[pl.Series, float]:
    return ((count_column / total) * 100).round(3)


def _add_percentage_of_transfers_column(dataframe: pl.DataFrame) -> pl.DataFrame:
    total_number_of_transfers = dataframe["count"].sum()
    dataframe["%_of_transfers"] = _calculate_percentage(
        dataframe["count"], total_number_of_transfers
    )
    return dataframe


def _add_percentage_of_technical_failures_column(dataframe: pl.DataFrame) -> pl.DataFrame:
    total_number_of_failed_transfers = dataframe.filter(
        col("status") == TransferStatus.TECHNICAL_FAILURE.value
    )["count"].sum()

    if total_number_of_failed_transfers is not None:
        dataframe = dataframe[
            [
                col("*"),
                (
                    when(col("status") == TransferStatus.TECHNICAL_FAILURE.value)
                    .then(
                        _calculate_percentage(dataframe["count"], total_number_of_failed_transfers)
                    )
                    .otherwise(None)
                    .alias("%_of_technical_failures")
                ),
            ]
        ]

    return dataframe


def count_outcomes_per_supplier_pathway(dataframe):
    outcome_counts_dataframe = (
        dataframe.with_columns(
            [
                col("final_error_codes").apply(_unique_errors).alias("unique_final_errors"),
                col("sender_error_codes").apply(_unique_errors).alias("unique_sender_errors"),
                col("intermediate_error_codes")
                .apply(_unique_errors)
                .alias("unique_intermediate_errors"),
            ]
        )
        .groupby(
            [
                "requesting_supplier",
                "sending_supplier",
                "status",
                "failure_reason",
                "unique_final_errors",
                "unique_sender_errors",
                "unique_intermediate_errors",
            ]
        )
        .agg([count("conversation_id").alias("count")])
        .sort(
            [col("count"), col("requesting_supplier"), col("sending_supplier"), col("status")],
            reverse=[True, False, False, False],
        )
    )

    outcome_counts_dataframe = _add_percentage_of_transfers_column(outcome_counts_dataframe)
    outcome_counts_dataframe = _add_percentage_of_technical_failures_column(
        outcome_counts_dataframe
    )

    return outcome_counts_dataframe
