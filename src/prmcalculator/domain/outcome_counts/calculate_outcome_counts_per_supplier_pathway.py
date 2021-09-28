import polars as pl
from polars import col


def _unique_errors(errors):
    return ",".join([str(e) for e in sorted(set(errors))])


def calculate_outcome_counts_per_supplier_pathway(dataframe: pl.DataFrame) -> pl.DataFrame:
    return dataframe.with_columns(
        [
            col("final_error_codes").apply(_unique_errors).alias("unique_final_errors"),
        ]
    ).select(
        [
            pl.col("requesting_supplier"),
            pl.col("sending_supplier"),
            pl.col("status"),
            pl.col("failure_reason"),
            pl.col("final_error_codes"),
            pl.col("unique_final_errors"),
        ]
    )
