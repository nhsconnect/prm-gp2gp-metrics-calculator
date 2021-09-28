import polars as pl
import pyarrow as pa
from dateutil.tz import UTC
from prmcalculator.domain.gp2gp.transfer import TransferStatus
from tests.builders.common import a_string, a_datetime, an_integer


def _int_list():
    return pa.list_(pa.int64())


def build_transfer_dataframe(**kwargs):
    return pl.from_arrow(
        pa.table(
            data={
                "conversation_id": [
                    kwargs.get("conversation_id", a_string(36)),
                ],
                "sla_duration": [kwargs.get("sla_duration", an_integer())],
                "requesting_practice_asid": [
                    kwargs.get("requesting_practice_asid", a_string(12)),
                ],
                "sending_practice_asid": [kwargs.get("sending_practice_asid", a_string(12))],
                "requesting_supplier": [kwargs.get("requesting_supplier", a_string(5))],
                "sending_supplier": [kwargs.get("sending_supplier", a_string(5))],
                "sender_error_codes": [kwargs.get("sender_error_codes", [])],
                "final_error_codes": [kwargs.get("final_error_codes", [])],
                "intermediate_error_codes": [kwargs.get("intermediate_error_codes", [])],
                "status": [kwargs.get("status", TransferStatus.INTEGRATED_ON_TIME.value)],
                "failure_reason": [kwargs.get("failure_reason", None)],
                "date_requested": [
                    kwargs.get("date_requested", a_datetime().astimezone(UTC)),
                ],
                "date_completed": [
                    kwargs.get("date_completed", a_datetime().astimezone(UTC)),
                ],
            },
            schema=pa.schema(
                [
                    ("conversation_id", pa.string()),
                    ("sla_duration", pa.uint64()),
                    ("requesting_practice_asid", pa.string()),
                    ("sending_practice_asid", pa.string()),
                    ("requesting_supplier", pa.string()),
                    ("sending_supplier", pa.string()),
                    ("sender_error_codes", _int_list()),
                    ("final_error_codes", _int_list()),
                    ("intermediate_error_codes", _int_list()),
                    ("status", pa.string()),
                    ("failure_reason", pa.string()),
                    ("date_requested", pa.timestamp("us")),
                    ("date_completed", pa.timestamp("us")),
                ]
            ),
        )
    )
