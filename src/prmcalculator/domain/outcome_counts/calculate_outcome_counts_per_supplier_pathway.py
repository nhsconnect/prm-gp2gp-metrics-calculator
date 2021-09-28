import polars as pl


def calculate_outcome_counts_per_supplier_pathway(dataframe: pl.DataFrame) -> pl.DataFrame:
    return dataframe.select(
        [
            pl.col("requesting_supplier"),
            pl.col("sending_supplier"),
            pl.col("status"),
            pl.col("failure_reason"),
        ]
    )
