from dataclasses import dataclass
from datetime import datetime
from typing import List, Iterable

from dateutil.tz import tzutc

from prmcalculator.domain.practice.metrics_calculator import PracticeMetrics
from prmcalculator.utils.calculate_percentage import calculate_percentage
from prmcalculator.domain.ods_portal.organisation_metadata import CcgDetails


@dataclass
class IntegratedPracticeMetricsPresentation:
    transfer_count: int
    within_3_days_percentage: float
    within_8_days_percentage: float
    beyond_8_days_percentage: float


@dataclass
class RequesterMetrics:
    integrated: IntegratedPracticeMetricsPresentation


@dataclass
class MonthlyMetricsPresentation:
    year: int
    month: int
    requester: RequesterMetrics


@dataclass
class PracticeSummary:
    ods_code: str
    name: str
    metrics: List[MonthlyMetricsPresentation]


@dataclass
class PracticeMetricsPresentation:
    generated_on: datetime
    practices: List[PracticeSummary]
    ccgs: List[CcgDetails]


def construct_practice_summaries(
    sla_metrics: Iterable[PracticeMetrics], year: int, month: int
) -> List[PracticeSummary]:
    return [
        PracticeSummary(
            ods_code=practice.ods_code,
            name=practice.name,
            metrics=[
                MonthlyMetricsPresentation(
                    year=year,
                    month=month,
                    requester=RequesterMetrics(
                        integrated=IntegratedPracticeMetricsPresentation(
                            transfer_count=practice.metrics[0].integrated.transfer_count,
                            within_3_days_percentage=calculate_percentage(
                                portion=practice.metrics[0].integrated.within_3_days,
                                total=practice.metrics[0].integrated.transfer_count,
                                num_digits=1,
                            ),
                            within_8_days_percentage=calculate_percentage(
                                portion=practice.metrics[0].integrated.within_8_days,
                                total=practice.metrics[0].integrated.transfer_count,
                                num_digits=1,
                            ),
                            beyond_8_days_percentage=calculate_percentage(
                                portion=practice.metrics[0].integrated.beyond_8_days,
                                total=practice.metrics[0].integrated.transfer_count,
                                num_digits=1,
                            ),
                        ),
                    ),
                )
            ],
        )
        for practice in sla_metrics
    ]


def construct_practice_metrics_presentation(
    practice_summaries: List[PracticeSummary],
    ccgs: List[CcgDetails],
) -> PracticeMetricsPresentation:
    return PracticeMetricsPresentation(
        generated_on=datetime.now(tzutc()), practices=practice_summaries, ccgs=ccgs
    )
