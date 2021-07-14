from dataclasses import dataclass
from typing import List, Iterable

from prmcalculator.domain.practice.metrics_calculator import PracticeMetrics
from prmcalculator.utils.calculate_percentage import calculate_percentage


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
class MonthlyMetrics:
    year: int
    month: int
    requester: RequesterMetrics


@dataclass
class PracticeSummary:
    ods_code: str
    name: str
    metrics: List[MonthlyMetrics]


def construct_practice_summaries(
    sla_metrics: Iterable[PracticeMetrics], year: int, month: int
) -> List[PracticeSummary]:
    return [
        PracticeSummary(
            ods_code=practice.ods_code,
            name=practice.name,
            metrics=[
                MonthlyMetrics(
                    year=year,
                    month=month,
                    requester=RequesterMetrics(
                        integrated=IntegratedPracticeMetricsPresentation(
                            transfer_count=practice.integrated.transfer_count,
                            within_3_days_percentage=calculate_percentage(
                                portion=practice.integrated.within_3_days,
                                total=practice.integrated.transfer_count,
                                num_digits=1,
                            ),
                            within_8_days_percentage=calculate_percentage(
                                portion=practice.integrated.within_8_days,
                                total=practice.integrated.transfer_count,
                                num_digits=1,
                            ),
                            beyond_8_days_percentage=calculate_percentage(
                                portion=practice.integrated.beyond_8_days,
                                total=practice.integrated.transfer_count,
                                num_digits=1,
                            ),
                        ),
                    ),
                )
            ],
        )
        for practice in sla_metrics
    ]
