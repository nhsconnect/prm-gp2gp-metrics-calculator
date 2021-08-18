from dataclasses import dataclass
from datetime import datetime
from typing import List, Iterable

from dateutil.tz import tzutc

from prmcalculator.domain.practice.deprecated.metrics_calculator_deprecated import (
    PracticeMetricsDeprecated,
)
from prmcalculator.utils.calculate_percentage import calculate_percentage
from prmcalculator.domain.ods_portal.organisation_metadata import CcgDetails


@dataclass
class IntegratedPracticeMetricsPresentationDeprecated:
    transfer_count: int
    within_3_days_percentage: float
    within_8_days_percentage: float
    beyond_8_days_percentage: float


@dataclass
class RequesterMetricsDeprecated:
    integrated: IntegratedPracticeMetricsPresentationDeprecated


@dataclass
class MonthlyMetricsPresentationDeprecated:
    year: int
    month: int
    requester: RequesterMetricsDeprecated


@dataclass
class PracticeSummaryDeprecated:
    ods_code: str
    name: str
    metrics: List[MonthlyMetricsPresentationDeprecated]


@dataclass
class PracticeMetricsPresentationDeprecated:
    generated_on: datetime
    practices: List[PracticeSummaryDeprecated]
    ccgs: List[CcgDetails]


def construct_practice_summaries_deprecated(
    sla_metrics: Iterable[PracticeMetricsDeprecated],
) -> List[PracticeSummaryDeprecated]:
    return [
        PracticeSummaryDeprecated(
            ods_code=practice.ods_code,
            name=practice.name,
            metrics=[
                MonthlyMetricsPresentationDeprecated(
                    year=metric.year,
                    month=metric.month,
                    requester=RequesterMetricsDeprecated(
                        integrated=IntegratedPracticeMetricsPresentationDeprecated(
                            transfer_count=metric.integrated.transfer_count,
                            within_3_days_percentage=calculate_percentage(
                                portion=metric.integrated.within_3_days,
                                total=metric.integrated.transfer_count,
                                num_digits=1,
                            ),
                            within_8_days_percentage=calculate_percentage(
                                portion=metric.integrated.within_8_days,
                                total=metric.integrated.transfer_count,
                                num_digits=1,
                            ),
                            beyond_8_days_percentage=calculate_percentage(
                                portion=metric.integrated.beyond_8_days,
                                total=metric.integrated.transfer_count,
                                num_digits=1,
                            ),
                        ),
                    ),
                )
                for metric in practice.metrics
            ],
        )
        for practice in sla_metrics
    ]


def construct_practice_metrics_presentation_deprecated(
    practice_summaries: List[PracticeSummaryDeprecated],
    ccgs: List[CcgDetails],
) -> PracticeMetricsPresentationDeprecated:
    return PracticeMetricsPresentationDeprecated(
        generated_on=datetime.now(tzutc()), practices=practice_summaries, ccgs=ccgs
    )
