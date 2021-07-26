from datetime import timedelta, datetime

from prmcalculator.domain.gp2gp.transfer import (
    convert_table_to_transfers,
    TransferOutcome,
    TransferStatus,
    TransferFailureReason,
    Transfer,
    Practice,
)
import pyarrow as pa

from tests.builders.common import a_string, a_datetime


def _build_transfer_table(**kwargs) -> pa.Table:
    return pa.Table.from_pydict(
        {
            "conversation_id": kwargs.get("conversation_id", [a_string(36)]),
            "sla_duration": kwargs.get("sla_duration", [1234]),
            "requesting_practice_asid": kwargs.get("requesting_practice_asid", [a_string(12)]),
            "sending_practice_asid": kwargs.get("sending_practice_asid", [a_string(12)]),
            "requesting_supplier": kwargs.get("requesting_supplier", [a_string(12)]),
            "sending_supplier": kwargs.get("sending_supplier", [a_string(12)]),
            "sender_error_code": kwargs.get("sender_error_code", [None]),
            "status": kwargs.get("status", ["INTEGRATED_ON_TIME"]),
            "failure_reason": kwargs.get("failure_reason", [""]),
            "date_requested": kwargs.get("date_requested", [a_datetime()]),
        }
    )


def test_conversation_id_column_is_converted_to_a_transfer_field():
    conversation_id = "123"

    table = _build_transfer_table(conversation_id=[conversation_id])

    transfers = convert_table_to_transfers(table)
    actual_conversation_id = next(iter(transfers)).conversation_id

    assert actual_conversation_id == conversation_id


def test_sla_duration_column_is_converted_to_timedelta():
    table = _build_transfer_table(sla_duration=[176586])
    transfers = convert_table_to_transfers(table)

    actual_sla_duration = next(iter(transfers)).sla_duration
    expected_sla_duration = timedelta(days=2, hours=1, minutes=3, seconds=6)

    assert actual_sla_duration == expected_sla_duration


def test_sla_duration_column_is_converted_to_a_transfer_field_if_none():
    table = _build_transfer_table(sla_duration=[None])
    transfers = convert_table_to_transfers(table)

    actual_sla_duration = next(iter(transfers)).sla_duration
    expected_sla_duration = None

    assert actual_sla_duration == expected_sla_duration


def test_requesting_practice_asid_column_is_converted_to_a_transfer_field():
    requesting_practice_asid = "121212121212"

    table = _build_transfer_table(requesting_practice_asid=[requesting_practice_asid])

    transfers = convert_table_to_transfers(table)
    actual_requesting_practice_asid = next(iter(transfers)).requesting_practice.asid

    assert actual_requesting_practice_asid == requesting_practice_asid


def test_sending_practice_asid_column_is_converted_to_a_transfer_field():
    sending_practice_asid = "172934718932"

    table = _build_transfer_table(sending_practice_asid=[sending_practice_asid])

    transfers = convert_table_to_transfers(table)
    actual_sending_practice_asid = next(iter(transfers)).sending_practice.asid

    assert actual_sending_practice_asid == sending_practice_asid


def test_requesting_supplier_column_is_converted_to_a_transfer_field():
    requesting_supplier = "EMIS Web"

    table = _build_transfer_table(requesting_supplier=[requesting_supplier])

    transfers = convert_table_to_transfers(table)
    actual_requesting_supplier = next(iter(transfers)).requesting_practice.supplier

    assert actual_requesting_supplier == requesting_supplier


def test_sending_supplier_column_is_converted_to_a_transfer_field():
    sending_supplier = "Vision"

    table = _build_transfer_table(sending_supplier=[sending_supplier])

    transfers = convert_table_to_transfers(table)
    actual_sending_supplier = next(iter(transfers)).sending_practice.supplier

    assert actual_sending_supplier == sending_supplier


def test_sender_error_code_column_is_converted_to_a_transfer_field():
    sender_error_code = 30

    table = _build_transfer_table(sender_error_code=[sender_error_code])

    transfers = convert_table_to_transfers(table)
    actual_sender_error_code = next(iter(transfers)).sender_error_code

    assert actual_sender_error_code == sender_error_code


def test_sender_error_code_column_is_converted_to_a_transfer_field_if_none():
    sender_error_code = None

    table = _build_transfer_table(sender_error_code=[sender_error_code])

    transfers = convert_table_to_transfers(table)
    actual_sender_error_code = next(iter(transfers)).sender_error_code

    assert actual_sender_error_code == sender_error_code


def test_status_and_failure_reason_columns_are_converted_to_a_transfer_outcome_field():
    table = _build_transfer_table(status=["TECHNICAL_FAILURE"], failure_reason=["Final Error"])

    transfers = convert_table_to_transfers(table)
    actual_transfer_outcome = next(iter(transfers)).outcome
    expected_transfer_outcome = TransferOutcome(
        status=TransferStatus.TECHNICAL_FAILURE, failure_reason=TransferFailureReason.FINAL_ERROR
    )

    assert actual_transfer_outcome == expected_transfer_outcome


def test_date_requested_column_is_converted_to_a_transfer_field():
    date_requested = a_datetime()

    table = _build_transfer_table(date_requested=[date_requested])

    transfers = convert_table_to_transfers(table)
    actual_date_requested = next(iter(transfers)).date_requested

    assert actual_date_requested == date_requested


def test_converts_multiple_rows_into_list_of_transfers():
    integrated_date_requested = a_datetime()
    integrated_sla_duration = timedelta(days=2, hours=19, minutes=0, seconds=41)

    table = _build_transfer_table(
        conversation_id=["123", "2345"],
        sla_duration=[241241, 12413],
        requesting_practice_asid=["213125436412", "124135423412"],
        sending_practice_asid=["123215421254", "234803124134"],
        requesting_supplier=["Vision", "Systm One"],
        sending_supplier=["EMIS Web", "Vision"],
        sender_error_code=[None, 30],
        status=["INTEGRATED_ON_TIME", "TECHNICAL_FAILURE"],
        failure_reason=[None, "Contains Fatal Sender Error"],
        date_requested=[integrated_date_requested, datetime(year=2021, month=12, day=1)],
    )

    expected_transfers = [
        Transfer(
            conversation_id="123",
            sla_duration=integrated_sla_duration,
            requesting_practice=Practice(asid="213125436412", supplier="Vision"),
            sending_practice=Practice(asid="123215421254", supplier="EMIS Web"),
            sender_error_code=None,
            outcome=TransferOutcome(status=TransferStatus.INTEGRATED_ON_TIME, failure_reason=None),
            date_requested=integrated_date_requested,
        ),
        Transfer(
            conversation_id="2345",
            sla_duration=timedelta(hours=3, minutes=26, seconds=53),
            requesting_practice=Practice(asid="124135423412", supplier="Systm One"),
            sending_practice=Practice(asid="234803124134", supplier="Vision"),
            sender_error_code=30,
            outcome=TransferOutcome(
                status=TransferStatus.TECHNICAL_FAILURE,
                failure_reason=TransferFailureReason.FATAL_SENDER_ERROR,
            ),
            date_requested=datetime(year=2021, month=12, day=1),
        ),
    ]

    actual_transfers = convert_table_to_transfers(table)

    assert actual_transfers == expected_transfers
