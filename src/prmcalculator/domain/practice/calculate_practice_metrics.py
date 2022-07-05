from dataclasses import dataclass
from datetime import datetime
from logging import Logger, getLogger
from typing import List

from dateutil.tz import tzutc

from prmcalculator.domain.gp2gp.transfer import Transfer
from prmcalculator.domain.practice.construct_practice_summary import (
    PracticeSummary,
    construct_practice_summary,
)
from prmcalculator.domain.practice.practice_transfer_metrics import PracticeTransferMetrics
from prmcalculator.domain.practice.transfer_service import ODSCode, TransfersService
from prmcalculator.domain.reporting_window import ReportingWindow

module_logger = getLogger(__name__)


class PracticeMetricsObservabilityProbe:
    def __init__(self, logger: Logger = module_logger):
        self._logger = logger

    def record_calculating_practice_metrics(self, reporting_window: ReportingWindow):
        self._logger.info(
            "Calculating practice metrics",
            extra={
                "event": "CALCULATING_PRACTICE_METRICS",
                "metric_months": reporting_window.metric_months,
            },
        )

    def record_unknown_practice_ods_code_for_transfer(self, transfer: Transfer):
        self._logger.warning(
            "Unknown practice ods_code for transfer, ignoring transfer from metrics",
            extra={
                "event": "UNKNOWN_PRACTICE_ODS_CODE_FOR_TRANSFER",
                "conversation_id": transfer.conversation_id,
                "asid": transfer.requesting_practice.asid,
            },
        )

    def record_unknown_practice_icb_ods_code_for_transfer(self, transfer: Transfer):
        self._logger.warning(
            "Unknown icb_ods_code for transfer, ignoring transfer from metrics",
            extra={
                "event": "UNKNOWN_ICB_ODS_CODE_FOR_TRANSFER",
                "conversation_id": transfer.conversation_id,
                "asid": transfer.requesting_practice.asid,
                "practice_ods_code": transfer.requesting_practice.ods_code,
            },
        )


@dataclass
class ICBPresentation:
    ods_code: ODSCode
    name: str
    practices: List[str]


@dataclass
class PracticeMetricsPresentation:
    generated_on: datetime
    practices: List[PracticeSummary]
    icbs: List[ICBPresentation]


def calculate_practice_metrics(
    transfers: List[Transfer],
    reporting_window: ReportingWindow,
    observability_probe: PracticeMetricsObservabilityProbe,
) -> PracticeMetricsPresentation:
    observability_probe.record_calculating_practice_metrics(reporting_window)

    transfers_service = TransfersService(
        transfers=transfers, observability_probe=observability_probe
    )

    return PracticeMetricsPresentation(
        generated_on=datetime.now(tzutc()),
        practices=[
            construct_practice_summary(
                practice_metrics=PracticeTransferMetrics.from_group(practice_transfers),
                reporting_window=reporting_window,
            )
            for practice_transfers in transfers_service.grouped_practices_by_ods
        ],
        icbs=[
            ICBPresentation(
                practices=transfer_by_icb.practices_ods_codes,
                name=transfer_by_icb.icb_name,
                ods_code=transfer_by_icb.icb_ods_code,
            )
            for transfer_by_icb in transfers_service.grouped_practices_by_icb
        ],
    )
