from dataclasses import dataclass
from datetime import timedelta, datetime
from enum import Enum
from typing import NamedTuple, Optional, List, Iterator

import pyarrow as pa


class TransferStatus(Enum):
    INTEGRATED_ON_TIME = "INTEGRATED_ON_TIME"
    TECHNICAL_FAILURE = "TECHNICAL_FAILURE"
    PROCESS_FAILURE = "PROCESS_FAILURE"
    UNCLASSIFIED_FAILURE = "UNCLASSIFIED_FAILURE"


class TransferFailureReason(Enum):
    INTEGRATED_LATE = "Integrated Late"
    FINAL_ERROR = "Final Error"
    TRANSFERRED_NOT_INTEGRATED = "Transferred, not integrated"
    REQUEST_NOT_ACKNOWLEDGED = "Request not Acknowledged"
    CORE_EHR_NOT_SENT = "Core Extract not Sent"
    FATAL_SENDER_ERROR = "Contains Fatal Sender Error"
    COPC_NOT_SENT = "COPC(s) not sent"
    COPC_NOT_ACKNOWLEDGED = "COPC(s) not Acknowledged"
    TRANSFERRED_NOT_INTEGRATED_WITH_ERROR = "TRANSFERRED_NOT_INTEGRATED_WITH_ERROR"
    AMBIGUOUS_COPCS = "Ambiguous COPC messages"


@dataclass
class TransferOutcome:
    status: TransferStatus
    failure_reason: Optional[TransferFailureReason]


@dataclass
class Practice:
    asid: str
    supplier: str


class Transfer(NamedTuple):
    conversation_id: str
    sla_duration: Optional[timedelta]
    requesting_practice: Practice
    sending_practice: Practice
    outcome: TransferOutcome
    date_requested: datetime


def filter_for_successful_transfers(transfers: List[Transfer]) -> Iterator[Transfer]:
    return (
        transfer
        for transfer in transfers
        if (
            transfer.outcome.status == TransferStatus.INTEGRATED_ON_TIME
            and transfer.sla_duration is not None
        )
        or (
            transfer.outcome.status == TransferStatus.PROCESS_FAILURE
            and transfer.outcome.failure_reason == TransferFailureReason.INTEGRATED_LATE
        )
    )


def _convert_to_timedelta(seconds: Optional[int]) -> Optional[timedelta]:
    if seconds is not None:
        return timedelta(seconds=seconds)
    else:
        return None


def _convert_pydict_to_list_of_dictionaries(pydict: dict):
    return (dict(zip(pydict.keys(), items)) for items in zip(*pydict.values()))


def convert_table_to_transfers(table: pa.Table) -> List[Transfer]:
    transfer_dict = table.to_pydict()

    transfers = _convert_pydict_to_list_of_dictionaries(transfer_dict)

    return [
        Transfer(
            conversation_id=transfer["conversation_id"],
            sla_duration=_convert_to_timedelta(transfer["sla_duration"]),
            requesting_practice=Practice(
                asid=transfer["requesting_practice_asid"], supplier=transfer["requesting_supplier"]
            ),
            sending_practice=Practice(
                asid=transfer["sending_practice_asid"], supplier=transfer["sending_supplier"]
            ),
            outcome=TransferOutcome(
                status=TransferStatus(transfer["status"]),
                failure_reason=TransferFailureReason(transfer["failure_reason"])
                if transfer["failure_reason"]
                else None,
            ),
            date_requested=transfer["date_requested"],
        )
        for transfer in transfers
    ]
