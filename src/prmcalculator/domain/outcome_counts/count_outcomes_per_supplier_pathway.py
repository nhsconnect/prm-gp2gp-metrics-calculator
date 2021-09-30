from typing import List, Optional
from polars import col, count  # type: ignore

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


def _unique_errors(errors: List[Optional[int]]):
    unique_error_codes = {error_code for error_code in errors if error_code is not None}
    return ", ".join(
        [f"{e} - {default_error_description_mapping[e]}" for e in sorted(unique_error_codes)]
    )


def count_outcomes_per_supplier_pathway(dataframe):
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
        .sort(
            [col("count"), col("requesting_supplier"), col("sending_supplier"), col("status")],
            reverse=[True, False, False, False],
        )
    )
