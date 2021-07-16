from datetime import timedelta
from typing import List

from prmcalculator.domain.gp2gp.transfer import (
    convert_table_to_transfers,
    TransferOutcome,
    TransferStatus,
    TransferFailureReason,
)
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


def test_requesting_practice_asid_column_is_converted_to_a_transfer_field():
    requesting_practice_asid = "121212121212"

    table = build_transfer_table(requesting_practice_asid=[requesting_practice_asid])

    transfers = convert_table_to_transfers(table)
    actual_requesting_practice_asid = transfers[0].requesting_practice_asid

    assert actual_requesting_practice_asid == requesting_practice_asid


def test_sending_practice_asid_column_is_converted_to_a_transfer_field():
    sending_practice_asid = "172934718932"

    table = build_transfer_table(sending_practice_asid=[sending_practice_asid])

    transfers = convert_table_to_transfers(table)
    actual_sending_practice_asid = transfers[0].sending_practice_asid

    assert actual_sending_practice_asid == sending_practice_asid


def test_requesting_practice_ods_code_column_is_converted_to_a_transfer_field():
    requesting_practice_ods_code = "A12345"

    table = build_transfer_table(requesting_practice_ods_code=[requesting_practice_ods_code])

    transfers = convert_table_to_transfers(table)
    actual_requesting_practice_ods_code = transfers[0].requesting_practice_ods_code

    assert actual_requesting_practice_ods_code == requesting_practice_ods_code


def test_sending_practice_ods_code_column_is_converted_to_a_transfer_field():
    sending_practice_ods_code = "A12345"

    table = build_transfer_table(sending_practice_ods_code=[sending_practice_ods_code])

    transfers = convert_table_to_transfers(table)
    actual_sending_practice_ods_code = transfers[0].sending_practice_ods_code

    assert actual_sending_practice_ods_code == sending_practice_ods_code


def test_requesting_supplier_column_is_converted_to_a_transfer_field():
    requesting_supplier = "EMIS Web"

    table = build_transfer_table(requesting_supplier=[requesting_supplier])

    transfers = convert_table_to_transfers(table)
    actual_requesting_supplier = transfers[0].requesting_supplier

    assert actual_requesting_supplier == requesting_supplier


def test_sending_supplier_column_is_converted_to_a_transfer_field():
    sending_supplier = "Vision"

    table = build_transfer_table(sending_supplier=[sending_supplier])

    transfers = convert_table_to_transfers(table)
    actual_sending_supplier = transfers[0].sending_supplier

    assert actual_sending_supplier == sending_supplier


def test_sender_error_code_column_is_converted_to_a_transfer_field():
    sender_error_code = 30

    table = build_transfer_table(sender_error_code=[sender_error_code])

    transfers = convert_table_to_transfers(table)
    actual_sender_error_code = transfers[0].sender_error_code

    assert actual_sender_error_code == sender_error_code


def test_sender_error_code_column_is_none():
    sender_error_code = None

    table = build_transfer_table(sender_error_code=[sender_error_code])

    transfers = convert_table_to_transfers(table)
    actual_sender_error_code = transfers[0].sender_error_code

    assert actual_sender_error_code == sender_error_code


def test_final_error_codes_column_is_converted_to_a_transfer_field():
    final_error_codes = [None, 12, 30]

    table = build_transfer_table(final_error_codes=[final_error_codes])

    transfers = convert_table_to_transfers(table)
    actual_final_error_codes = transfers[0].final_error_codes

    assert actual_final_error_codes == final_error_codes


def test_final_error_codes_column_is_converted_to_a_transfer_field_when_empty():
    final_error_codes: List[int] = []

    table = build_transfer_table(final_error_codes=[final_error_codes])

    transfers = convert_table_to_transfers(table)
    actual_final_error_codes = transfers[0].final_error_codes

    assert actual_final_error_codes == final_error_codes


def test_intermediate_error_codes_column_is_converted_to_a_transfer_field():
    intermediate_error_codes = [16, 17]

    table = build_transfer_table(intermediate_error_codes=[intermediate_error_codes])

    transfers = convert_table_to_transfers(table)
    actual_intermediate_error_codes = transfers[0].intermediate_error_codes

    assert actual_intermediate_error_codes == intermediate_error_codes


def test_intermediate_error_codes_column_is_converted_to_a_transfer_field_when_empty():
    intermediate_error_codes: List[int] = []

    table = build_transfer_table(intermediate_error_codes=[intermediate_error_codes])

    transfers = convert_table_to_transfers(table)
    actual_intermediate_error_codes = transfers[0].intermediate_error_codes

    assert actual_intermediate_error_codes == intermediate_error_codes


def test_status_and_failure_reason_columns_are_converted_to_a_transfer_outcome_field():
    table = build_transfer_table(status=["TECHNICAL_FAILURE"], failure_reason=["Final Error"])

    transfers = convert_table_to_transfers(table)
    actual_transfer_outcome = transfers[0].transfer_outcome
    expected_transfer_outcome = TransferOutcome(
        status=TransferStatus.TECHNICAL_FAILURE, reason=TransferFailureReason.FINAL_ERROR
    )

    assert actual_transfer_outcome == expected_transfer_outcome
