from datetime import datetime

from dateutil.tz import tzutc
from freezegun import freeze_time

from prmcalculator.domain.national.calculate_national_metrics_data import (
    calculate_national_metrics_data,
)
from prmcalculator.domain.national.construct_national_metrics_presentation import (
    NationalMetricsPresentation,
    NationalMetricMonthPresentation,
    OutcomeMetricsPresentation,
    ProcessFailureMetricsPresentation,
    PaperFallbackMetricsPresentation,
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
def test_calculates_correct_national_metrics_given_series_of_transfers():
    metric_month_start = a_datetime(year=2019, month=12, day=1)
    transfers_integrated_on_time = [
        a_transfer_integrated_within_3_days(),
        a_transfer_integrated_between_3_and_8_days(),
        a_transfer_integrated_between_3_and_8_days(),
    ]
    transfers_unclassified_error = [
        a_transfer_where_a_copc_triggered_an_error(),
    ]
    transfers_technical_failure = [
        a_transfer_where_the_request_was_never_acknowledged(),
        a_transfer_where_no_core_ehr_was_sent(),
        a_transfer_where_no_copc_continue_was_sent(),
        a_transfer_where_copc_fragments_were_required_but_not_sent(),
        a_transfer_where_copc_fragments_remained_unacknowledged(),
        a_transfer_where_the_sender_reported_an_unrecoverable_error(),
        a_transfer_with_a_final_error(),
    ]

    transfers_process_failure = [
        a_transfer_integrated_beyond_8_days(),
        a_transfer_integrated_beyond_8_days(),
        a_transfer_integrated_beyond_8_days(),
        a_transfer_that_was_never_integrated(),
    ]
    transfers = (
        transfers_process_failure
        + transfers_integrated_on_time
        + transfers_technical_failure
        + transfers_unclassified_error
    )

    reporting_window = MonthlyReportingWindow(
        date_anchor_month_start=a_datetime(year=2020, month=1, day=1),
        metric_monthly_datetimes=[metric_month_start],
    )
    current_datetime = datetime.now(tzutc())

    expected_national_metrics_month_presentation = NationalMetricMonthPresentation(
        year=2019,
        month=12,
        transfer_count=15,
        integrated_on_time=OutcomeMetricsPresentation(
            transfer_count=3,
            transfer_percentage=20.0,
        ),
        paper_fallback=PaperFallbackMetricsPresentation(
            transfer_count=12,
            transfer_percentage=80.0,
            process_failure=ProcessFailureMetricsPresentation(
                transfer_count=4,
                transfer_percentage=26.67,
                integrated_late=OutcomeMetricsPresentation(
                    transfer_count=3,
                    transfer_percentage=20.0,
                ),
                transferred_not_integrated=OutcomeMetricsPresentation(
                    transfer_count=1,
                    transfer_percentage=6.67,
                ),
            ),
            technical_failure=OutcomeMetricsPresentation(
                transfer_count=7,
                transfer_percentage=46.67,
            ),
            unclassified_failure=OutcomeMetricsPresentation(
                transfer_count=1,
                transfer_percentage=6.67,
            ),
        ),
    )

    expected_national_metrics = NationalMetricsPresentation(
        generated_on=current_datetime, metrics=[expected_national_metrics_month_presentation]
    )

    actual = calculate_national_metrics_data(transfers=transfers, reporting_window=reporting_window)

    assert actual == expected_national_metrics


@freeze_time(datetime(year=2020, month=1, day=17, hour=21, second=32), tz_offset=0)
def test_calculates_correct_national_metrics_for_transfers_within_reporting_window():
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

    expected_national_metrics_month_presentation = NationalMetricMonthPresentation(
        year=2019,
        month=12,
        transfer_count=1,
        integrated_on_time=OutcomeMetricsPresentation(
            transfer_count=1,
            transfer_percentage=100.0,
        ),
        paper_fallback=PaperFallbackMetricsPresentation(
            transfer_count=0,
            transfer_percentage=0.0,
            process_failure=ProcessFailureMetricsPresentation(
                transfer_count=0,
                transfer_percentage=0.0,
                integrated_late=OutcomeMetricsPresentation(
                    transfer_count=0,
                    transfer_percentage=0.0,
                ),
                transferred_not_integrated=OutcomeMetricsPresentation(
                    transfer_count=0,
                    transfer_percentage=0.0,
                ),
            ),
            technical_failure=OutcomeMetricsPresentation(
                transfer_count=0,
                transfer_percentage=0.0,
            ),
            unclassified_failure=OutcomeMetricsPresentation(
                transfer_count=0,
                transfer_percentage=0.0,
            ),
        ),
    )

    expected_national_metrics = NationalMetricsPresentation(
        generated_on=current_datetime, metrics=[expected_national_metrics_month_presentation]
    )

    actual = calculate_national_metrics_data(transfers=transfers, reporting_window=reporting_window)

    assert actual == expected_national_metrics
