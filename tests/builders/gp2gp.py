from datetime import timedelta

from prmcalculator.domain.gp2gp.sla import EIGHT_DAYS_IN_SECONDS, THREE_DAYS_IN_SECONDS
from prmcalculator.domain.gp2gp.transfer import (
    Practice,
    Transfer,
    TransferFailureReason,
    TransferOutcome,
    TransferStatus,
)
from tests.builders.common import a_datetime, a_duration, a_string


def build_transfer(**kwargs) -> Transfer:
    date_requested = kwargs.get("date_requested", a_datetime())
    return Transfer(
        conversation_id=kwargs.get("conversation_id", a_string(36)),
        sla_duration=kwargs.get("sla_duration", a_duration()),
        requesting_practice=kwargs.get(
            "requesting_practice", Practice(asid=a_string(12), supplier=a_string(12))
        ),
        outcome=kwargs.get(
            "outcome",
            TransferOutcome(status=TransferStatus.INTEGRATED_ON_TIME, failure_reason=None),
        ),
        date_requested=date_requested,
        last_sender_message_timestamp=kwargs.get(
            "last_sender_message_timestamp", date_requested + timedelta(minutes=1)
        ),
    )


def an_integrated_transfer(**kwargs):
    return build_transfer(
        outcome=TransferOutcome(status=TransferStatus.INTEGRATED_ON_TIME, failure_reason=None),
        sla_duration=kwargs.get("sla_duration", a_duration(max_length=604800)),
    )


def a_supressed_transfer(**kwargs):
    return build_transfer(
        outcome=TransferOutcome(
            status=TransferStatus.INTEGRATED_ON_TIME,
            failure_reason=None,
        ),
        final_error_codes=[15],
        sla_duration=kwargs.get("sla_duration", a_duration(max_length=604800)),
    )


def a_transfer_integrated_within_3_days(**kwargs):
    date_requested = kwargs.get("date_requested", a_datetime())

    return build_transfer(
        outcome=TransferOutcome(status=TransferStatus.INTEGRATED_ON_TIME, failure_reason=None),
        sla_duration=timedelta(seconds=THREE_DAYS_IN_SECONDS),
        requesting_practice=kwargs.get(
            "requesting_practice", Practice(asid=a_string(12), supplier=a_string(12))
        ),
        date_requested=kwargs.get("date_requested", a_datetime()),
        last_sender_message_timestamp=kwargs.get(
            "last_sender_message_timestamp", date_requested + timedelta(minutes=1)
        ),
    )


def a_transfer_integrated_between_3_and_8_days(**kwargs):
    return build_transfer(
        outcome=TransferOutcome(status=TransferStatus.INTEGRATED_ON_TIME, failure_reason=None),
        sla_duration=timedelta(seconds=THREE_DAYS_IN_SECONDS + 1),
        date_requested=kwargs.get("date_requested", a_datetime()),
    )


def a_transfer_integrated_beyond_8_days(**kwargs):
    return build_transfer(
        outcome=TransferOutcome(
            status=TransferStatus.PROCESS_FAILURE,
            failure_reason=TransferFailureReason.INTEGRATED_LATE,
        ),
        sla_duration=timedelta(seconds=EIGHT_DAYS_IN_SECONDS + 1),
        requesting_practice=kwargs.get(
            "requesting_practice", Practice(asid=a_string(12), supplier=a_string(12))
        ),
        date_requested=kwargs.get("date_requested", a_datetime()),
    )


def a_transfer_with_a_final_error(**kwargs):
    return build_transfer(
        outcome=TransferOutcome(
            status=TransferStatus.TECHNICAL_FAILURE,
            failure_reason=TransferFailureReason.FINAL_ERROR,
        ),
        date_requested=kwargs.get("date_requested", a_datetime()),
    )


def a_transfer_that_was_never_integrated(**kwargs):
    date_requested = kwargs.get("date_requested", a_datetime())

    return Transfer(
        sla_duration=None,
        outcome=TransferOutcome(
            status=TransferStatus.PROCESS_FAILURE,
            failure_reason=TransferFailureReason.TRANSFERRED_NOT_INTEGRATED,
        ),
        conversation_id=kwargs.get("conversation_id", a_string(36)),
        requesting_practice=kwargs.get(
            "requesting_practice", Practice(asid=a_string(12), supplier=a_string(12))
        ),
        date_requested=date_requested,
        last_sender_message_timestamp=kwargs.get(
            "last_sender_message_timestamp", date_requested + timedelta(minutes=1)
        ),
    )


def a_transfer_where_the_request_was_never_acknowledged(**kwargs):
    return build_transfer(
        outcome=TransferOutcome(
            status=TransferStatus.TECHNICAL_FAILURE,
            failure_reason=TransferFailureReason.REQUEST_NOT_ACKNOWLEDGED,
        ),
        date_requested=kwargs.get("date_requested", a_datetime()),
    )


def a_transfer_where_no_core_ehr_was_sent(**kwargs):
    date_requested = kwargs.get("date_requested", a_datetime())
    return build_transfer(
        outcome=TransferOutcome(
            status=TransferStatus.TECHNICAL_FAILURE,
            failure_reason=TransferFailureReason.CORE_EHR_NOT_SENT,
        ),
        requesting_practice=kwargs.get(
            "requesting_practice", Practice(asid=a_string(12), supplier=a_string(12))
        ),
        date_requested=date_requested,
        last_sender_message_timestamp=kwargs.get(
            "last_sender_message_timestamp", date_requested + timedelta(minutes=1)
        ),
    )


def a_transfer_where_no_copc_continue_was_sent(**kwargs):
    return build_transfer(
        outcome=TransferOutcome(
            status=TransferStatus.TECHNICAL_FAILURE,
            failure_reason=TransferFailureReason.COPC_NOT_SENT,
        ),
        date_requested=kwargs.get("date_requested", a_datetime()),
    )


def a_transfer_where_copc_fragments_were_required_but_not_sent(**kwargs):
    return build_transfer(
        outcome=TransferOutcome(
            status=TransferStatus.TECHNICAL_FAILURE,
            failure_reason=TransferFailureReason.COPC_NOT_SENT,
        ),
        date_requested=kwargs.get("date_requested", a_datetime()),
    )


def a_transfer_where_copc_fragments_remained_unacknowledged(**kwargs):
    return build_transfer(
        outcome=TransferOutcome(
            status=TransferStatus.TECHNICAL_FAILURE,
            failure_reason=TransferFailureReason.COPC_NOT_ACKNOWLEDGED,
        ),
        date_requested=kwargs.get("date_requested", a_datetime()),
    )


def a_transfer_where_the_sender_reported_an_unrecoverable_error(**kwargs):
    return build_transfer(
        outcome=TransferOutcome(
            status=TransferStatus.TECHNICAL_FAILURE,
            failure_reason=TransferFailureReason.FATAL_SENDER_ERROR,
        ),
        date_requested=kwargs.get("date_requested", a_datetime()),
    )


def a_transfer_where_a_copc_triggered_an_error(**kwargs):
    return build_transfer(
        outcome=TransferOutcome(
            status=TransferStatus.UNCLASSIFIED_FAILURE,
            failure_reason=TransferFailureReason.TRANSFERRED_NOT_INTEGRATED_WITH_ERROR,
        ),
        date_requested=kwargs.get("date_requested", a_datetime()),
    )
