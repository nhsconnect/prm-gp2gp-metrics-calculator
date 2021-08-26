from datetime import timedelta

from prmcalculator.domain.ods_portal.organisation_metadata import PracticeDetails

from prmcalculator.domain.gp2gp.sla import EIGHT_DAYS_IN_SECONDS, THREE_DAYS_IN_SECONDS
from prmcalculator.domain.gp2gp.transfer import (
    Transfer,
    TransferStatus,
    TransferOutcome,
    TransferFailureReason,
    Practice,
)
from tests.builders.common import a_string, a_duration, a_datetime


def build_practice_details(**kwargs) -> PracticeDetails:
    return PracticeDetails(
        name=kwargs.get("name", a_string()),
        ods_code=kwargs.get("ods_code", a_string()),
        asids=kwargs.get("asids", []),
    )


def build_transfer(**kwargs) -> Transfer:
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
        date_requested=kwargs.get("date_requested", a_datetime(year=2019, month=12, day=4)),
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
    return build_transfer(
        outcome=TransferOutcome(status=TransferStatus.INTEGRATED_ON_TIME, failure_reason=None),
        sla_duration=timedelta(seconds=THREE_DAYS_IN_SECONDS),
        requesting_practice=kwargs.get(
            "requesting_practice", Practice(asid=a_string(12), supplier=a_string(12))
        ),
        date_requested=kwargs.get("date_requested", a_datetime(year=2019, month=12, day=4)),
    )


def a_transfer_integrated_between_3_and_8_days():
    return build_transfer(
        outcome=TransferOutcome(status=TransferStatus.INTEGRATED_ON_TIME, failure_reason=None),
        sla_duration=timedelta(seconds=THREE_DAYS_IN_SECONDS + 1),
    )


def a_transfer_integrated_beyond_8_days():
    return build_transfer(
        outcome=TransferOutcome(
            status=TransferStatus.PROCESS_FAILURE,
            failure_reason=TransferFailureReason.INTEGRATED_LATE,
        ),
        sla_duration=timedelta(seconds=EIGHT_DAYS_IN_SECONDS + 1),
    )


def a_transfer_with_a_final_error():
    return build_transfer(
        outcome=TransferOutcome(
            status=TransferStatus.TECHNICAL_FAILURE,
            failure_reason=TransferFailureReason.FINAL_ERROR,
        )
    )


def a_transfer_that_was_never_integrated(**kwargs):
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
        date_requested=kwargs.get("date_requested", a_datetime(year=2019, month=12, day=4)),
    )


def a_transfer_where_the_request_was_never_acknowledged():
    return build_transfer(
        outcome=TransferOutcome(
            status=TransferStatus.TECHNICAL_FAILURE,
            failure_reason=TransferFailureReason.REQUEST_NOT_ACKNOWLEDGED,
        )
    )


def a_transfer_where_no_core_ehr_was_sent():
    return build_transfer(
        outcome=TransferOutcome(
            status=TransferStatus.TECHNICAL_FAILURE,
            failure_reason=TransferFailureReason.CORE_EHR_NOT_SENT,
        )
    )


def a_transfer_where_no_copc_continue_was_sent():
    return build_transfer(
        outcome=TransferOutcome(
            status=TransferStatus.TECHNICAL_FAILURE,
            failure_reason=TransferFailureReason.COPC_NOT_SENT,
        )
    )


def a_transfer_where_copc_fragments_were_required_but_not_sent():
    return build_transfer(
        outcome=TransferOutcome(
            status=TransferStatus.TECHNICAL_FAILURE,
            failure_reason=TransferFailureReason.COPC_NOT_SENT,
        )
    )


def a_transfer_where_copc_fragments_remained_unacknowledged():
    return build_transfer(
        outcome=TransferOutcome(
            status=TransferStatus.TECHNICAL_FAILURE,
            failure_reason=TransferFailureReason.COPC_NOT_ACKNOWLEDGED,
        )
    )


def a_transfer_where_the_sender_reported_an_unrecoverable_error():
    return build_transfer(
        outcome=TransferOutcome(
            status=TransferStatus.TECHNICAL_FAILURE,
            failure_reason=TransferFailureReason.FATAL_SENDER_ERROR,
        )
    )


def a_transfer_where_a_copc_triggered_an_error():
    return build_transfer(
        outcome=TransferOutcome(
            status=TransferStatus.UNCLASSIFIED_FAILURE,
            failure_reason=TransferFailureReason.TRANSFERRED_NOT_INTEGRATED_WITH_ERROR,
        )
    )
