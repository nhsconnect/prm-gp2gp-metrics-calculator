from typing import List, Optional, Union
import polars as pl
from polars import col, count, when, first, sum  # type: ignore

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
    total_number_of_transfers = dataframe["number of transfers"].sum()
    dataframe["% of transfers"] = _calculate_percentage(
        dataframe["number of transfers"], total_number_of_transfers
    )
    return dataframe


def _add_percentage_of_technical_failures_column(dataframe: pl.DataFrame) -> pl.DataFrame:
    total_number_of_failed_transfers = dataframe.filter(
        col("status") == TransferStatus.TECHNICAL_FAILURE.value
    )["number of transfers"].sum()

    if total_number_of_failed_transfers is not None:
        dataframe = dataframe[
            [
                col("*"),
                (
                    when(col("status") == TransferStatus.TECHNICAL_FAILURE.value)
                    .then(
                        _calculate_percentage(
                            dataframe["number of transfers"], total_number_of_failed_transfers
                        )
                    )
                    .otherwise(None)
                    .alias("% of technical failures")
                ),
            ]
        ]

    return dataframe


def _get_supplier_pathway_count(
    requesting_supplier: str, sending_supplier: str, supplier_pathway_counts: pl.DataFrame
) -> int:
    count_df = supplier_pathway_counts.filter(
        col("requesting supplier") == requesting_supplier
    ).filter(col("sending supplier") == sending_supplier)
    return first(count_df["supplier pathway count"])


def _add_percentage_of_supplier_pathway_column(dataframe) -> pl.DataFrame:
    supplier_pathway_counts = dataframe.groupby(["requesting supplier", "sending supplier"]).agg(
        [sum("number of transfers").alias("supplier pathway count")]
    )
    dataframe["% of supplier pathway"] = dataframe.apply(
        lambda row: round(
            row[7] / _get_supplier_pathway_count(row[0], row[1], supplier_pathway_counts) * 100, 3
        )
    )
    return dataframe


def count_outcomes_per_supplier_pathway(dataframe):
    outcome_counts_dataframe = (
        dataframe.with_columns(
            [
                col("requesting_supplier").alias("requesting supplier"),
                col("sending_supplier").alias("sending supplier"),
                col("failure_reason").alias("failure reason"),
                col("final_error_codes").apply(_unique_errors).alias("unique final errors"),
                col("sender_error_codes").apply(_unique_errors).alias("unique sender errors"),
                col("intermediate_error_codes")
                .apply(_unique_errors)
                .alias("unique intermediate errors"),
            ]
        )
        .groupby(
            [
                "requesting supplier",
                "sending supplier",
                "status",
                "failure reason",
                "unique final errors",
                "unique sender errors",
                "unique intermediate errors",
            ]
        )
        .agg([count("conversation_id").alias("number of transfers")])
        .sort(
            [
                col("number of transfers"),
                col("requesting supplier"),
                col("sending supplier"),
                col("status"),
            ],
            reverse=[True, False, False, False],
        )
    )

    outcome_counts_dataframe = _add_percentage_of_transfers_column(outcome_counts_dataframe)
    outcome_counts_dataframe = _add_percentage_of_technical_failures_column(
        outcome_counts_dataframe
    )
    outcome_counts_dataframe = _add_percentage_of_supplier_pathway_column(outcome_counts_dataframe)

    return outcome_counts_dataframe
