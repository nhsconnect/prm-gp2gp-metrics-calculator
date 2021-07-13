from dataclasses import dataclass
from datetime import timedelta, datetime
from enum import Enum
from typing import NamedTuple, Optional, List, Iterator


class TransferStatus(Enum):
    INTEGRATED_ON_TIME = "INTEGRATED_ON_TIME"
    TECHNICAL_FAILURE = "TECHNICAL_FAILURE"
    PENDING = "PENDING"
    PENDING_WITH_ERROR = "PENDING_WITH_ERROR"
    PROCESS_FAILURE = "PROCESS_FAILURE"
    TRANSFERRED_NOT_INTEGRATED_WITH_ERROR = "TRANSFERRED_NOT_INTEGRATED_WITH_ERROR"


class TransferFailureReason(Enum):
    INTEGRATED_LATE = "Integrated Late"
    FINAL_ERROR = "Final Error"
    TRANSFERRED_NOT_INTEGRATED = "Transferred, not integrated"
    REQUEST_NOT_ACKNOWLEDGED = "Request not Acknowledged"
    CORE_EHR_NOT_SENT = "Core Extract not Sent"
    FATAL_SENDER_ERROR = "Contains Fatal Sender Error"
    COPC_NOT_SENT = "COPC(s) not sent"
    COPC_NOT_ACKNOWLEDGED = "COPC(s) not Acknowledged"
    DEFAULT = ""


@dataclass
class TransferOutcome:
    status: TransferStatus
    reason: TransferFailureReason


class Transfer(NamedTuple):
    conversation_id: str
    sla_duration: Optional[timedelta]
    requesting_practice_asid: str
    sending_practice_asid: str
    requesting_practice_ods_code: str
    sending_practice_ods_code: str
    requesting_supplier: str
    sending_supplier: str
    sender_error_code: Optional[int]
    final_error_codes: List[Optional[int]]
    intermediate_error_codes: List[int]
    transfer_outcome: TransferOutcome
    date_requested: datetime
    date_completed: Optional[datetime]


def filter_for_successful_transfers(transfers: List[Transfer]) -> Iterator[Transfer]:
    return (
        transfer
        for transfer in transfers
        if (
            transfer.transfer_outcome.status == TransferStatus.INTEGRATED_ON_TIME
            and transfer.sla_duration is not None
        )
        or (
            transfer.transfer_outcome.status == TransferStatus.PROCESS_FAILURE
            and transfer.transfer_outcome.reason == TransferFailureReason.INTEGRATED_LATE
        )
    )
