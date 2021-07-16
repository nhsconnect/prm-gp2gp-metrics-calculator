from prmcalculator.domain.practice.metrics_calculator import (
    PracticeMetrics,
    IntegratedPracticeMetrics,
)
from prmcalculator.domain.gp2gp.transfer import (
    Transfer,
    TransferOutcome,
    TransferStatus,
    TransferFailureReason,
)
from tests.builders.common import a_string, a_duration, a_datetime, an_integer


def build_transfer(**kwargs) -> Transfer:
    return Transfer(
        conversation_id=kwargs.get("conversation_id", a_string(36)),
        sla_duration=kwargs.get("sla_duration", a_duration()),
        requesting_practice_asid=kwargs.get("requesting_practice_asid", a_string(12)),
        sending_practice_asid=kwargs.get("sending_practice_asid", a_string(12)),
        requesting_practice_ods_code=kwargs.get("requesting_practice_ods_code", a_string(6)),
        sending_practice_ods_code=kwargs.get("sending_practice_ods_code", a_string(6)),
        requesting_supplier=kwargs.get("requesting_supplier", a_string(12)),
        sending_supplier=kwargs.get("sending_supplier", a_string(12)),
        sender_error_code=kwargs.get("sender_error_code", None),
        final_error_codes=kwargs.get("final_error_codes", []),
        intermediate_error_codes=kwargs.get("intermediate_error_codes", []),
        transfer_outcome=kwargs.get(
            "transfer_outcome",
            TransferOutcome(status=TransferStatus.PENDING, reason=TransferFailureReason.DEFAULT),
        ),
        date_requested=kwargs.get("date_requested", a_datetime()),
        date_completed=kwargs.get("date_completed", None),
    )


def build_practice_metrics(**kwargs) -> PracticeMetrics:
    return PracticeMetrics(
        ods_code=kwargs.get("ods_code", a_string(6)),
        name=kwargs.get("name", a_string()),
        integrated=IntegratedPracticeMetrics(
            transfer_count=kwargs.get("transfer_count", an_integer()),
            within_3_days=kwargs.get("within_3_days", an_integer()),
            within_8_days=kwargs.get("within_8_days", an_integer()),
            beyond_8_days=kwargs.get("beyond_8_days", an_integer()),
        ),
    )
