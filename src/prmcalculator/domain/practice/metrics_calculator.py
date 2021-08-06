from dataclasses import dataclass
from typing import Iterable, Iterator, List
from warnings import warn

from prmcalculator.domain.practice.practice_lookup import PracticeLookup
from prmcalculator.domain.gp2gp.sla import SlaCounter
from prmcalculator.domain.gp2gp.transfer import Transfer
from prmcalculator.utils.reporting_window import MonthlyReportingWindow


@dataclass
class IntegratedPracticeMetrics:
    transfer_count: int
    within_3_days: int
    within_8_days: int
    beyond_8_days: int


@dataclass
class MonthlyMetrics:
    year: int
    month: int
    integrated: IntegratedPracticeMetrics


@dataclass
class PracticeMetrics:
    ods_code: str
    name: str
    metrics: List[MonthlyMetrics]


def _derive_practice_sla_metrics(practice, sla_metrics):
    return PracticeMetrics(
        practice.ods_code,
        practice.name,
        metrics=[
            MonthlyMetrics(
                year=year,
                month=month,
                integrated=IntegratedPracticeMetrics(
                    transfer_count=metrics.total(),
                    within_3_days=metrics.within_3_days,
                    within_8_days=metrics.within_8_days,
                    beyond_8_days=metrics.beyond_8_days,
                ),
            )
            for (year, month), metrics in sla_metrics.items()
        ],
    )


def _create_practice_monthly_counts(
    practice_lookup: PracticeLookup, reporting_window: MonthlyReportingWindow
):
    def _monthly_sla_counters():
        return {metric_month: SlaCounter() for metric_month in reporting_window.metric_months}

    return {ods_code: _monthly_sla_counters() for ods_code in practice_lookup.all_ods_codes()}


def calculate_monthly_sla_by_practice(
    practice_lookup: PracticeLookup,
    transfers: Iterable[Transfer],
    reporting_window: MonthlyReportingWindow,
) -> Iterator[PracticeMetrics]:
    practice_counts = _create_practice_monthly_counts(practice_lookup, reporting_window)

    unexpected_asids = set()
    for transfer in transfers:
        asid = transfer.requesting_practice.asid

        if practice_lookup.has_asid_code(asid):
            request_started_metric_month = (
                transfer.date_requested.year,
                transfer.date_requested.month,
            )
            ods_code = practice_lookup.ods_code_from_asid(asid)
            practice_counts[ods_code][request_started_metric_month].increment(transfer.sla_duration)
        else:
            unexpected_asids.add(asid)

    if len(unexpected_asids) > 0:
        warn(f"Unexpected ASID count: {len(unexpected_asids)}", RuntimeWarning)

    return (
        _derive_practice_sla_metrics(practice, practice_counts[practice.ods_code])
        for practice in practice_lookup.all_practices()
    )
