from datetime import datetime

from dateutil.tz import tzutc
from freezegun import freeze_time

from prmcalculator.domain.national.deprecated.calculate_national_metrics_data_deprecated import (
    calculate_national_metrics_data_deprecated,
)
from prmcalculator.domain.national.deprecated.metrics_presentation_deprecated import (
    MonthlyNationalMetricsDeprecated,
    IntegratedMetricsPresentationDeprecated,
    FailedMetricsDeprecated,
    PendingMetricsDeprecated,
    PaperFallbackMetricsDeprecated,
    NationalMetricsPresentationDeprecated,
)
from prmcalculator.utils.reporting_window import MonthlyReportingWindow
from tests.builders.common import a_duration, a_datetime
from tests.builders.gp2gp import (
    a_transfer_integrated_beyond_8_days,
    a_transfer_integrated_within_3_days,
    a_transfer_integrated_between_3_and_8_days,
    a_transfer_with_a_final_error,
    a_transfer_that_was_never_integrated,
    a_transfer_where_the_request_was_never_acknowledged,
    a_transfer_where_no_core_ehr_was_sent,
    a_transfer_where_no_copc_continue_was_sent,
    a_transfer_where_copc_fragments_were_required_but_not_sent,
    a_transfer_where_copc_fragments_remained_unacknowledged,
    a_transfer_where_the_sender_reported_an_unrecoverable_error,
    a_transfer_where_a_copc_triggered_an_error,
    build_transfer,
)


@freeze_time(datetime(year=2020, month=1, day=17, hour=21, second=32), tz_offset=0)
def test_calculates_correct_national_metrics_given_series_of_transfers_deprecated():
    metric_month_start = a_datetime(year=2019, month=12, day=1)

    transfers = [
        a_transfer_that_was_never_integrated(),
        a_transfer_where_the_request_was_never_acknowledged(),
        a_transfer_where_no_core_ehr_was_sent(),
        a_transfer_where_no_copc_continue_was_sent(),
        a_transfer_where_copc_fragments_were_required_but_not_sent(),
        a_transfer_where_copc_fragments_remained_unacknowledged(),
        a_transfer_where_the_sender_reported_an_unrecoverable_error(),
        a_transfer_where_a_copc_triggered_an_error(),
        a_transfer_integrated_within_3_days(),
        a_transfer_integrated_between_3_and_8_days(),
        a_transfer_integrated_between_3_and_8_days(),
        a_transfer_integrated_beyond_8_days(),
        a_transfer_integrated_beyond_8_days(),
        a_transfer_integrated_beyond_8_days(),
        a_transfer_with_a_final_error(),
    ]

    reporting_window = MonthlyReportingWindow(
        date_anchor_month_start=a_datetime(year=2020, month=1, day=1),
        metric_monthly_datetimes=[metric_month_start],
    )
    current_datetime = datetime.now(tzutc())

    expected_national_metrics = MonthlyNationalMetricsDeprecated(
        transfer_count=15,
        integrated=IntegratedMetricsPresentationDeprecated(
            transfer_percentage=40.0,
            transfer_count=6,
            within_3_days=1,
            within_8_days=2,
            beyond_8_days=3,
        ),
        failed=FailedMetricsDeprecated(transfer_count=1, transfer_percentage=6.67),
        pending=PendingMetricsDeprecated(transfer_count=8, transfer_percentage=53.33),
        paper_fallback=PaperFallbackMetricsDeprecated(transfer_count=12, transfer_percentage=80.0),
        year=2019,
        month=12,
    )

    expected = NationalMetricsPresentationDeprecated(
        generated_on=current_datetime, metrics=[expected_national_metrics]
    )
    actual = calculate_national_metrics_data_deprecated(transfers, reporting_window)

    assert actual == expected


@freeze_time(datetime(year=2020, month=1, day=17, hour=21, second=32), tz_offset=0)
def test_calculates_correct_national_metrics_for_transfers_within_reporting_window_deprecated():
    metric_month_start = a_datetime(year=2019, month=12, day=1)

    transfer_within_reporting_window = build_transfer(
        date_requested=a_datetime(year=2019, month=12, day=14), sla_duration=a_duration(600)
    )
    transfer_before_reporting_window = build_transfer(
        date_requested=a_datetime(year=2019, month=11, day=10)
    )
    transfer_after_reporting_window = build_transfer(
        date_requested=a_datetime(year=2020, month=1, day=4)
    )

    transfers = [
        transfer_within_reporting_window,
        transfer_before_reporting_window,
        transfer_after_reporting_window,
    ]

    reporting_window = MonthlyReportingWindow(
        date_anchor_month_start=a_datetime(year=2020, month=1, day=1),
        metric_monthly_datetimes=[metric_month_start],
    )
    current_datetime = datetime.now(tzutc())

    expected_national_metrics = MonthlyNationalMetricsDeprecated(
        transfer_count=1,
        integrated=IntegratedMetricsPresentationDeprecated(
            transfer_percentage=100.0,
            transfer_count=1,
            within_3_days=1,
            within_8_days=0,
            beyond_8_days=0,
        ),
        failed=FailedMetricsDeprecated(transfer_count=0, transfer_percentage=0.0),
        pending=PendingMetricsDeprecated(transfer_count=0, transfer_percentage=0.0),
        paper_fallback=PaperFallbackMetricsDeprecated(transfer_count=0, transfer_percentage=0.0),
        year=2019,
        month=12,
    )

    expected = NationalMetricsPresentationDeprecated(
        generated_on=current_datetime, metrics=[expected_national_metrics]
    )
    actual = calculate_national_metrics_data_deprecated(transfers, reporting_window)

    assert actual == expected
