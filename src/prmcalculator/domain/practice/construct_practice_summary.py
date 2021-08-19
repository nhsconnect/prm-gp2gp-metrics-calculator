from dataclasses import dataclass
from typing import List

from prmcalculator.domain.practice.practice_transfer_metrics import PracticeTransferMetrics
from prmcalculator.utils.calculate_percentage import calculate_percentage
from prmcalculator.utils.reporting_window import MonthlyReportingWindow


@dataclass
class IntegratedPracticeMetricsPresentation:
    transfer_count: int
    within_3_days_percentage: float
    within_8_days_percentage: float
    beyond_8_days_percentage: float


@dataclass
class AwaitingIntegration:
    percentage: float


@dataclass
class TransfersReceivedPresentation:
    transfer_count: int
    awaiting_integration: AwaitingIntegration
    integrated: IntegratedPracticeMetricsPresentation


@dataclass
class RequesterMetrics:
    integrated: IntegratedPracticeMetricsPresentation
    transfers_received: TransfersReceivedPresentation


@dataclass
class MonthlyMetricsPresentation:
    year: int
    month: int
    requester: RequesterMetrics


@dataclass
class PracticeSummary:
    ods_code: str
    metrics: List[MonthlyMetricsPresentation]


def construct_practice_summary(
    transfer_metrics: PracticeTransferMetrics, reporting_window: MonthlyReportingWindow
) -> PracticeSummary:
    return PracticeSummary(
        ods_code=transfer_metrics.ods_code,
        metrics=[
            MonthlyMetricsPresentation(
                year=metric_month[0],
                month=metric_month[1],
                requester=RequesterMetrics(
                    integrated=IntegratedPracticeMetricsPresentation(
                        transfer_count=transfer_metrics.transfer_metrics[
                            metric_month
                        ].integrated_total(),
                        within_3_days_percentage=calculate_percentage(
                            portion=transfer_metrics.transfer_metrics[
                                metric_month
                            ].integrated_within_3_days(),
                            total=transfer_metrics.transfer_metrics[
                                metric_month
                            ].integrated_total(),
                        ),
                        within_8_days_percentage=calculate_percentage(
                            portion=transfer_metrics.transfer_metrics[
                                metric_month
                            ].integrated_within_8_days(),
                            total=transfer_metrics.transfer_metrics[
                                metric_month
                            ].integrated_total(),
                        ),
                        beyond_8_days_percentage=calculate_percentage(
                            portion=transfer_metrics.transfer_metrics[
                                metric_month
                            ].integrated_beyond_8_days(),
                            total=transfer_metrics.transfer_metrics[
                                metric_month
                            ].integrated_total(),
                        ),
                    ),
                    transfers_received=TransfersReceivedPresentation(
                        transfer_count=transfer_metrics.transfer_metrics[
                            metric_month
                        ].received_by_practice_total(),
                        awaiting_integration=AwaitingIntegration(
                            percentage=calculate_percentage(
                                portion=transfer_metrics.transfer_metrics[
                                    metric_month
                                ].process_failure_not_integrated(),
                                total=transfer_metrics.transfer_metrics[
                                    metric_month
                                ].received_by_practice_total(),
                            )
                        ),
                        integrated=IntegratedPracticeMetricsPresentation(
                            transfer_count=transfer_metrics.transfer_metrics[
                                metric_month
                            ].integrated_total(),
                            within_3_days_percentage=calculate_percentage(
                                portion=transfer_metrics.transfer_metrics[
                                    metric_month
                                ].integrated_within_3_days(),
                                total=transfer_metrics.transfer_metrics[
                                    metric_month
                                ].received_by_practice_total(),
                            ),
                            within_8_days_percentage=calculate_percentage(
                                portion=transfer_metrics.transfer_metrics[
                                    metric_month
                                ].integrated_within_8_days(),
                                total=transfer_metrics.transfer_metrics[
                                    metric_month
                                ].received_by_practice_total(),
                            ),
                            beyond_8_days_percentage=calculate_percentage(
                                portion=transfer_metrics.transfer_metrics[
                                    metric_month
                                ].integrated_beyond_8_days(),
                                total=transfer_metrics.transfer_metrics[
                                    metric_month
                                ].received_by_practice_total(),
                            ),
                        ),
                    ),
                ),
            )
            for metric_month in reporting_window.metric_months
        ],
    )
