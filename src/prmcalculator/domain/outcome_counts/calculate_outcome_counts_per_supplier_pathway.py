from typing import List, Optional
import polars as pl
from polars import col, count  # type: ignore


def _unique_errors(errors: List[Optional[int]]):
    unique_error_codes = {error_code for error_code in errors if error_code is not None}
    return ",".join([str(e) for e in sorted(unique_error_codes)])


def calculate_outcome_counts_per_supplier_pathway(dataframe: pl.DataFrame):
    return (
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
        .sort("count", reverse=True)
    )
