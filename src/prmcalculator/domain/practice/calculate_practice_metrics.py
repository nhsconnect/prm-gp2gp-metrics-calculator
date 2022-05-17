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
from prmcalculator.domain.practice.group_transfers_by_ccg import ODSCode, group_transfers_by_ccg
from prmcalculator.domain.practice.group_transfers_by_practice import group_transfers_by_practice
from prmcalculator.domain.practice.practice_transfer_metrics import PracticeTransferMetrics
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

    def record_unknown_practice_for_transfer(self, transfer: Transfer):
        self._logger.warning(
            "Unknown practice for transfer",
            extra={
                "event": "UNKNOWN_PRACTICE_FOR_TRANSFER",
                "conversation_id": transfer.conversation_id,
                "unknown_asid": transfer.requesting_practice.asid,
            },
        )


@dataclass
class CCGPresentation:
    ods_code: ODSCode
    name: str
    practices: List[str]


@dataclass
class PracticeMetricsPresentation:
    generated_on: datetime
    practices: List[PracticeSummary]
    ccgs: List[CCGPresentation]


def calculate_practice_metrics(
    transfers: List[Transfer],
    reporting_window: ReportingWindow,
    observability_probe: PracticeMetricsObservabilityProbe,
) -> PracticeMetricsPresentation:
    observability_probe.record_calculating_practice_metrics(reporting_window)

    grouped_transfers_by_practice = group_transfers_by_practice(
        transfers=transfers,
        observability_probe=observability_probe,
    )

    grouped_transfers_by_ccg = group_transfers_by_ccg(
        practices=grouped_transfers_by_practice,
        observability_probe=observability_probe,
    )

    return PracticeMetricsPresentation(
        generated_on=datetime.now(tzutc()),
        practices=[
            construct_practice_summary(
                practice_metrics=PracticeTransferMetrics.from_group(practice_transfers),
                reporting_window=reporting_window,
            )
            for practice_transfers in grouped_transfers_by_practice
        ],
        ccgs=[
            CCGPresentation(
                practices=transfer_by_ccg.practices_ods_codes,
                name=transfer_by_ccg.ccg_name,
                ods_code=transfer_by_ccg.ccg_ods_code,
            )
            for transfer_by_ccg in grouped_transfers_by_ccg
        ],
    )
