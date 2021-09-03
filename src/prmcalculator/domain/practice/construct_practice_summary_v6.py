from dataclasses import dataclass
from typing import List

from prmcalculator.domain.ods_portal.organisation_metadata import PracticeDetails
from prmcalculator.domain.practice.practice_transfer_metrics import PracticeTransferMetrics
from prmcalculator.utils.reporting_window import MonthlyReportingWindow


@dataclass
class MonthlyMetricsPresentation:
    year: int
    month: int


@dataclass
class PracticeSummary:
    name: str
    ods_code: str
    metrics: List[MonthlyMetricsPresentation]


def construct_practice_summary(
    practice_details: PracticeDetails,
    practice_metrics: PracticeTransferMetrics,
    reporting_window: MonthlyReportingWindow,
) -> PracticeSummary:
    return PracticeSummary(
        name=practice_details.name,
        ods_code=practice_details.ods_code,
        metrics=[
            MonthlyMetricsPresentation(
                year=reporting_window.metric_months[0][0],
                month=reporting_window.metric_months[0][1],
            )
        ],
    )
