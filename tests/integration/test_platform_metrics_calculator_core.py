from datetime import datetime, timedelta

from dateutil.tz import UTC, tzutc
from freezegun import freeze_time

from prmcalculator.domain.national.metrics_presentation import (
    MonthlyNationalMetrics,
    IntegratedMetricsPresentation,
    FailedMetrics,
    PendingMetrics,
    PaperFallbackMetrics,
    NationalMetricsPresentation,
)
from prmcalculator.domain.practice.metrics_presentation import (
    IntegratedPracticeMetricsPresentation,
    RequesterMetrics,
    MonthlyMetricsPresentation,
    PracticeSummary,
    PracticeMetricsPresentation,
)
from prmcalculator.domain.ods_portal.organisation_metadata import (
    PracticeDetails,
    CcgDetails,
    OrganisationMetadata,
)
from prmcalculator.pipeline.core import (
    calculate_practice_metrics_data,
    calculate_national_metrics_data,
)

from prmcalculator.domain.gp2gp.transfer import (
    Transfer,
    TransferStatus,
    TransferOutcome,
    Practice,
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


@freeze_time(datetime(year=2020, month=1, day=15, hour=23, second=42), tz_offset=0)
def test_calculates_correct_practice_metrics_given_a_successful_transfer():
    metric_month_start = datetime(2019, 12, 1, tzinfo=UTC)

    reporting_window = MonthlyReportingWindow(
        date_anchor_month_start=datetime(2020, 1, 1, tzinfo=UTC),
        metric_monthly_datetimes=[metric_month_start],
    )

    requesting_practice_name = "Test GP"
    requesting_ods_code = "A12345"
    requesting_practice = Practice(asid="343434343434", supplier="SystemOne")
    conversation_id = "abcdefg_1234"
    ccg_ods_code = "23B"
    ccg_name = "Test CCG"

    transfers = [
        Transfer(
            conversation_id=conversation_id,
            sla_duration=timedelta(days=1, seconds=52707),
            requesting_practice=requesting_practice,
            outcome=TransferOutcome(failure_reason=None, status=TransferStatus.INTEGRATED_ON_TIME),
            date_requested=datetime(2019, 12, 30, 18, 2, 29, tzinfo=UTC),
        )
    ]

    practice_list = [
        PracticeDetails(
            asids=[requesting_practice.asid],
            ods_code=requesting_ods_code,
            name=requesting_practice_name,
        )
    ]

    ccg_list = [CcgDetails(name=ccg_name, ods_code=ccg_ods_code, practices=[requesting_ods_code])]

    organisation_metadata = OrganisationMetadata(
        generated_on=datetime(year=2020, month=1, day=15, hour=23, second=42, tzinfo=UTC),
        practices=practice_list,
        ccgs=ccg_list,
    )

    expected = PracticeMetricsPresentation(
        generated_on=datetime(year=2020, month=1, day=15, hour=23, second=42, tzinfo=UTC),
        practices=[
            PracticeSummary(
                ods_code=requesting_ods_code,
                name=requesting_practice_name,
                metrics=[
                    MonthlyMetricsPresentation(
                        year=2019,
                        month=12,
                        requester=RequesterMetrics(
                            integrated=IntegratedPracticeMetricsPresentation(
                                transfer_count=1,
                                within_3_days_percentage=100,
                                within_8_days_percentage=0,
                                beyond_8_days_percentage=0,
                            ),
                        ),
                    )
                ],
            )
        ],
        ccgs=ccg_list,
    )

    actual = calculate_practice_metrics_data(transfers, organisation_metadata, reporting_window)

    assert actual == expected


@freeze_time(datetime(year=2020, month=1, day=17, hour=21, second=32), tz_offset=0)
def test_calculates_correct_national_metrics_given_series_of_transfers():
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

    expected_national_metrics = MonthlyNationalMetrics(
        transfer_count=15,
        integrated=IntegratedMetricsPresentation(
            transfer_percentage=40.0,
            transfer_count=6,
            within_3_days=1,
            within_8_days=2,
            beyond_8_days=3,
        ),
        failed=FailedMetrics(transfer_count=1, transfer_percentage=6.67),
        pending=PendingMetrics(transfer_count=8, transfer_percentage=53.33),
        paper_fallback=PaperFallbackMetrics(transfer_count=12, transfer_percentage=80.0),
        year=2019,
        month=12,
    )

    expected = NationalMetricsPresentation(
        generated_on=current_datetime, metrics=[expected_national_metrics]
    )
    actual = calculate_national_metrics_data(transfers, reporting_window)

    assert actual == expected


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

    expected_national_metrics = MonthlyNationalMetrics(
        transfer_count=1,
        integrated=IntegratedMetricsPresentation(
            transfer_percentage=100.0,
            transfer_count=1,
            within_3_days=1,
            within_8_days=0,
            beyond_8_days=0,
        ),
        failed=FailedMetrics(transfer_count=0, transfer_percentage=0.0),
        pending=PendingMetrics(transfer_count=0, transfer_percentage=0.0),
        paper_fallback=PaperFallbackMetrics(transfer_count=0, transfer_percentage=0.0),
        year=2019,
        month=12,
    )

    expected = NationalMetricsPresentation(
        generated_on=current_datetime, metrics=[expected_national_metrics]
    )
    actual = calculate_national_metrics_data(transfers, reporting_window)

    assert actual == expected
