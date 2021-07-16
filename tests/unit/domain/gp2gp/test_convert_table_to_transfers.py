from datetime import timedelta

from prmcalculator.domain.gp2gp.transfer import convert_table_to_transfers
import pyarrow as pa

from tests.builders.common import a_string, a_datetime


def build_transfer_table(**kwargs) -> pa.Table:
    return pa.Table.from_pydict(
        {
            "conversation_id": kwargs.get("conversation_id", [a_string(36)]),
            "sla_duration": kwargs.get("sla_duration", [1234]),
            "requesting_practice_asid": kwargs.get("requesting_practice_asid", [a_string(12)]),
            "sending_practice_asid": kwargs.get("sending_practice_asid", [a_string(12)]),
            "requesting_practice_ods_code": kwargs.get(
                "requesting_practice_ods_code", [a_string(6)]
            ),
            "sending_practice_ods_code": kwargs.get("sending_practice_ods_code", [a_string(6)]),
            "requesting_supplier": kwargs.get("requesting_supplier", [a_string(12)]),
            "sending_supplier": kwargs.get("sending_supplier", [a_string(12)]),
            "sender_error_code": kwargs.get("sender_error_code", [None]),
            "final_error_codes": kwargs.get("final_error_codes", [[]]),
            "intermediate_error_codes": kwargs.get("intermediate_error_codes", [[]]),
            "status": kwargs.get("status", ["INTEGRATED_ON_TIME"]),
            "failure_reason": kwargs.get("failure_reason", [""]),
            "date_requested": kwargs.get("date_requested", [a_datetime()]),
            "date_completed": kwargs.get("date_completed", [None]),
        }
    )


def test_conversation_id_column_is_converted_to_a_transfer_field():
    conversation_id = "123"

    table = build_transfer_table(conversation_id=[conversation_id])

    transfers = convert_table_to_transfers(table)
    actual_conversation_id = transfers[0].conversation_id

    assert actual_conversation_id == conversation_id


def test_sla_duration_column_is_converted_to_timedelta():
    table = build_transfer_table(sla_duration=[176586])
    transfers = convert_table_to_transfers(table)

    actual_sla_duration = transfers[0].sla_duration
    expected_sla_duration = timedelta(days=2, hours=1, minutes=3, seconds=6)

    assert actual_sla_duration == expected_sla_duration


def test_sla_duration_column_is_none():
    table = build_transfer_table(sla_duration=[None])
    transfers = convert_table_to_transfers(table)

    actual_sla_duration = transfers[0].sla_duration
    expected_sla_duration = None

    assert actual_sla_duration == expected_sla_duration
