from dataclasses import dataclass
from datetime import timedelta, datetime
from enum import Enum
from typing import NamedTuple, Optional, List, Iterator, Iterable

import pyarrow as Table


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


def _convert_to_timedelta(seconds: Optional[int]) -> Optional[timedelta]:
    if seconds is not None:
        return timedelta(seconds=seconds)
    else:
        return None


def convert_table_to_transfers(table: Table) -> Iterable[Transfer]:
    transfer_dict = table.to_pydict()

    transfer_list = []

    for i in range(0, len(transfer_dict["conversation_id"])):
        transfer_list.append(
            Transfer(
                conversation_id=transfer_dict["conversation_id"][i],
                sla_duration=_convert_to_timedelta(transfer_dict["sla_duration"][i]),
                requesting_practice_asid=transfer_dict["requesting_practice_asid"][i],
                sending_practice_asid=transfer_dict["sending_practice_asid"][i],
                requesting_practice_ods_code=transfer_dict["requesting_practice_ods_code"][i],
                sending_practice_ods_code=transfer_dict["sending_practice_ods_code"][i],
                requesting_supplier=transfer_dict["requesting_supplier"][i],
                sending_supplier=transfer_dict["sending_supplier"][i],
                sender_error_code=transfer_dict["sender_error_code"][i],
                final_error_codes=transfer_dict["final_error_codes"][i],
                intermediate_error_codes=transfer_dict["intermediate_error_codes"][i],
                transfer_outcome=TransferOutcome(
                    status=TransferStatus(transfer_dict["status"][i]),
                    reason=TransferFailureReason(transfer_dict["failure_reason"][i]),
                ),
                date_requested=transfer_dict["date_requested"][i],
                date_completed=transfer_dict["date_completed"][i],
            )
        )

    return transfer_list
