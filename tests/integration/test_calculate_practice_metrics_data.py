from datetime import datetime, timedelta
from unittest.mock import Mock

from dateutil.tz import UTC
from freezegun import freeze_time

from prmcalculator.domain.ods_portal.organisation_metadata import (
    CcgMetadata,
    OrganisationMetadata,
    PracticeMetadata,
)
from prmcalculator.domain.practice.calculate_practice_metrics import (
    PracticeMetricsPresentation,
    calculate_practice_metrics,
)
from prmcalculator.domain.practice.construct_practice_summary import (
    MonthlyMetricsPresentation,
    PracticeSummary,
    RequestedTransferMetrics,
)
from prmcalculator.domain.reporting_window import ReportingWindow
from tests.builders.common import a_datetime
from tests.builders.gp2gp import (
    a_transfer_integrated_within_3_days,
    a_transfer_that_was_never_integrated,
    a_transfer_where_no_core_ehr_was_sent,
    build_practice,
)


@freeze_time(datetime(year=2020, month=1, day=15, hour=23, second=42), tz_offset=0)
def test_calculates_correct_practice_metrics_given_transfers():
    mock_probe = Mock()
    metric_month_start = a_datetime(year=2019, month=12, day=1)

    reporting_window = ReportingWindow(
        date_anchor_month_start=a_datetime(year=2020, month=1, day=1),
        dates=[],
        metric_months_datetimes=[metric_month_start],
    )

    requesting_practice_name = "Test GP"
    requesting_ods_code = "A12345"
    requesting_practice = build_practice(asid="343434343434", supplier="SystemOne")
    ccg_ods_code = "23B"
    ccg_name = "Test CCG"

    transfers = [
        a_transfer_integrated_within_3_days(
            requesting_practice=requesting_practice,
            date_requested=datetime(2019, 12, 30, 18, 2, 29, tzinfo=UTC),
        ),
        a_transfer_that_was_never_integrated(
            requesting_practice=requesting_practice,
            date_requested=datetime(2019, 12, 30, 18, 2, 29, tzinfo=UTC),
        ),
    ]

    practice_list = [
        PracticeMetadata(
            asids=[requesting_practice.asid],
            ods_code=requesting_ods_code,
            name=requesting_practice_name,
        )
    ]

    ccg_list = [CcgMetadata(name=ccg_name, ods_code=ccg_ods_code, practices=[requesting_ods_code])]

    organisation_metadata = OrganisationMetadata(
        generated_on=datetime(year=2020, month=1, day=15, hour=23, second=42, tzinfo=UTC),
        practices=practice_list,
        ccgs=ccg_list,
    )

    expected = PracticeMetricsPresentation(
        generated_on=datetime(year=2020, month=1, day=15, hour=23, second=42, tzinfo=UTC),
        practices=[
            PracticeSummary(
                name=requesting_practice_name,
                ods_code=requesting_ods_code,
                metrics=[
                    MonthlyMetricsPresentation(
                        year=2019,
                        month=12,
                        requested_transfers=RequestedTransferMetrics(
                            requested_count=2,
                            received_count=2,
                            integrated_within_3_days_count=1,
                            integrated_within_8_days_count=0,
                            received_percent_of_requested=100.00,
                            integrated_within_3_days_percent_of_received=50.00,
                            integrated_within_8_days_percent_of_received=0,
                            not_integrated_within_8_days_total=1,
                            not_integrated_within_8_days_percent_of_received=50.00,
                            failures_total_count=0,
                            failures_total_percent_of_requested=0,
                        ),
                    )
                ],
            )
        ],
        ccgs=ccg_list,
    )

    actual = calculate_practice_metrics(
        transfers=transfers,
        organisation_metadata=organisation_metadata,
        reporting_window=reporting_window,
        observability_probe=mock_probe,
    )

    assert actual == expected


@freeze_time(datetime(year=2020, month=1, day=15, hour=23, second=42), tz_offset=0)
def test_returns_default_metric_values_for_practice_without_transfers():
    mock_probe = Mock()
    metric_month_start = a_datetime(year=2019, month=12, day=1)

    reporting_window = ReportingWindow(
        date_anchor_month_start=a_datetime(year=2020, month=1, day=1),
        dates=[],
        metric_months_datetimes=[metric_month_start],
    )

    requesting_practice_name = "Test GP practice with no transfers"
    requesting_ods_code = "A4656"

    practice_list = [
        PracticeMetadata(
            asids=["12431"],
            ods_code=requesting_ods_code,
            name=requesting_practice_name,
        )
    ]

    organisation_metadata = OrganisationMetadata(
        generated_on=datetime(year=2020, month=1, day=15, hour=23, second=42, tzinfo=UTC),
        practices=practice_list,
        ccgs=[],
    )

    expected = PracticeMetricsPresentation(
        generated_on=datetime(year=2020, month=1, day=15, hour=23, second=42, tzinfo=UTC),
        practices=[
            PracticeSummary(
                name=requesting_practice_name,
                ods_code=requesting_ods_code,
                metrics=[
                    MonthlyMetricsPresentation(
                        year=2019,
                        month=12,
                        requested_transfers=RequestedTransferMetrics(
                            requested_count=0,
                            received_count=0,
                            integrated_within_3_days_count=0,
                            integrated_within_8_days_count=0,
                            received_percent_of_requested=None,
                            integrated_within_3_days_percent_of_received=None,
                            integrated_within_8_days_percent_of_received=None,
                            not_integrated_within_8_days_total=0,
                            not_integrated_within_8_days_percent_of_received=None,
                            failures_total_count=0,
                            failures_total_percent_of_requested=None,
                        ),
                    )
                ],
            )
        ],
        ccgs=[],
    )

    actual = calculate_practice_metrics(
        transfers=[],
        organisation_metadata=organisation_metadata,
        reporting_window=reporting_window,
        observability_probe=mock_probe,
    )

    assert actual == expected


def test_calls_observability_probe_calculating_practice_metrics():
    mock_probe = Mock()

    reporting_window = ReportingWindow(
        date_anchor_month_start=a_datetime(),
        dates=[],
        metric_months_datetimes=[a_datetime()],
    )

    organisation_metadata = OrganisationMetadata(
        generated_on=a_datetime(),
        practices=[],
        ccgs=[],
    )

    calculate_practice_metrics(
        transfers=[],
        organisation_metadata=organisation_metadata,
        reporting_window=reporting_window,
        observability_probe=mock_probe,
    )

    mock_probe.record_calculating_practice_metrics.assert_called_once_with(reporting_window)


@freeze_time(datetime(year=2020, month=1, day=15, hour=23, second=42), tz_offset=0)
def test_calculates_correct_practice_metrics_filtering_transfers_that_take_longer_than_config_day():
    mock_probe = Mock()
    metric_month_start = a_datetime(year=2019, month=12, day=1)

    reporting_window = ReportingWindow(
        date_anchor_month_start=a_datetime(year=2020, month=1, day=1),
        dates=[],
        metric_months_datetimes=[metric_month_start],
    )

    requesting_practice_name = "Test GP"
    requesting_ods_code = "A12345"
    requesting_practice = build_practice(asid="343434343434", supplier="SystemOne")
    ccg_ods_code = "23B"
    ccg_name = "Test CCG"

    date_requested = datetime(2019, 12, 30, 18, 2, 29, tzinfo=UTC)
    transferred_within_a_day_timestamp = date_requested + timedelta(hours=1)
    transferred_longer_than_a_day_timestamp = date_requested + timedelta(days=1, hours=1)

    transfers = [
        a_transfer_integrated_within_3_days(
            requesting_practice=requesting_practice,
            date_requested=date_requested,
            last_sender_message_timestamp=transferred_within_a_day_timestamp,
        ),
        a_transfer_integrated_within_3_days(
            requesting_practice=requesting_practice,
            date_requested=date_requested,
            last_sender_message_timestamp=transferred_longer_than_a_day_timestamp,
        ),
        a_transfer_that_was_never_integrated(
            requesting_practice=requesting_practice,
            date_requested=date_requested,
            last_sender_message_timestamp=transferred_within_a_day_timestamp,
        ),
        a_transfer_that_was_never_integrated(
            requesting_practice=requesting_practice,
            date_requested=date_requested,
            last_sender_message_timestamp=transferred_longer_than_a_day_timestamp,
        ),
        a_transfer_that_was_never_integrated(
            requesting_practice=requesting_practice,
            date_requested=date_requested,
            last_sender_message_timestamp=transferred_longer_than_a_day_timestamp,
        ),
        a_transfer_where_no_core_ehr_was_sent(
            requesting_practice=requesting_practice,
            date_requested=date_requested,
            last_sender_message_timestamp=None,
        ),
    ]

    practice_list = [
        PracticeMetadata(
            asids=[requesting_practice.asid],
            ods_code=requesting_ods_code,
            name=requesting_practice_name,
        )
    ]

    ccg_list = [CcgMetadata(name=ccg_name, ods_code=ccg_ods_code, practices=[requesting_ods_code])]

    organisation_metadata = OrganisationMetadata(
        generated_on=datetime(year=2020, month=1, day=15, hour=23, second=42, tzinfo=UTC),
        practices=practice_list,
        ccgs=ccg_list,
    )

    expected = PracticeMetricsPresentation(
        generated_on=datetime(year=2020, month=1, day=15, hour=23, second=42, tzinfo=UTC),
        practices=[
            PracticeSummary(
                name=requesting_practice_name,
                ods_code=requesting_ods_code,
                metrics=[
                    MonthlyMetricsPresentation(
                        year=2019,
                        month=12,
                        requested_transfers=RequestedTransferMetrics(
                            requested_count=3,
                            received_count=2,
                            integrated_within_3_days_count=1,
                            integrated_within_8_days_count=0,
                            received_percent_of_requested=66.7,
                            integrated_within_3_days_percent_of_received=50.0,
                            integrated_within_8_days_percent_of_received=0.0,
                            not_integrated_within_8_days_total=1,
                            not_integrated_within_8_days_percent_of_received=50.0,
                            failures_total_count=1,
                            failures_total_percent_of_requested=33.3,
                        ),
                    )
                ],
            )
        ],
        ccgs=ccg_list,
    )

    actual = calculate_practice_metrics(
        transfers=transfers,
        organisation_metadata=organisation_metadata,
        reporting_window=reporting_window,
        observability_probe=mock_probe,
        hide_slow_transferred_records_after_days=1,
    )

    assert actual == expected


@freeze_time(datetime(year=2020, month=1, day=15, hour=23, second=42), tz_offset=0)
def test_calculates_correct_practice_metrics_without_filtering_transfers_if_config_day_not_set():
    mock_probe = Mock()
    metric_month_start = a_datetime(year=2019, month=12, day=1)

    reporting_window = ReportingWindow(
        date_anchor_month_start=a_datetime(year=2020, month=1, day=1),
        dates=[],
        metric_months_datetimes=[metric_month_start],
    )

    requesting_practice_name = "Test GP"
    requesting_ods_code = "A12345"
    requesting_practice = build_practice(asid="343434343434", supplier="SystemOne")
    ccg_ods_code = "23B"
    ccg_name = "Test CCG"

    date_requested = datetime(2019, 12, 30, 18, 2, 29, tzinfo=UTC)
    transferred_within_a_day_timestamp = date_requested + timedelta(hours=1)
    transferred_longer_than_a_day_timestamp = date_requested + timedelta(days=1, hours=1)

    transfers = [
        a_transfer_integrated_within_3_days(
            requesting_practice=requesting_practice,
            date_requested=date_requested,
            last_sender_message_timestamp=transferred_within_a_day_timestamp,
        ),
        a_transfer_integrated_within_3_days(
            requesting_practice=requesting_practice,
            date_requested=date_requested,
            last_sender_message_timestamp=transferred_longer_than_a_day_timestamp,
        ),
        a_transfer_that_was_never_integrated(
            requesting_practice=requesting_practice,
            date_requested=date_requested,
            last_sender_message_timestamp=transferred_within_a_day_timestamp,
        ),
        a_transfer_that_was_never_integrated(
            requesting_practice=requesting_practice,
            date_requested=date_requested,
            last_sender_message_timestamp=transferred_longer_than_a_day_timestamp,
        ),
        a_transfer_that_was_never_integrated(
            requesting_practice=requesting_practice,
            date_requested=date_requested,
            last_sender_message_timestamp=transferred_longer_than_a_day_timestamp,
        ),
    ]

    practice_list = [
        PracticeMetadata(
            asids=[requesting_practice.asid],
            ods_code=requesting_ods_code,
            name=requesting_practice_name,
        )
    ]

    ccg_list = [CcgMetadata(name=ccg_name, ods_code=ccg_ods_code, practices=[requesting_ods_code])]

    organisation_metadata = OrganisationMetadata(
        generated_on=datetime(year=2020, month=1, day=15, hour=23, second=42, tzinfo=UTC),
        practices=practice_list,
        ccgs=ccg_list,
    )

    expected = PracticeMetricsPresentation(
        generated_on=datetime(year=2020, month=1, day=15, hour=23, second=42, tzinfo=UTC),
        practices=[
            PracticeSummary(
                name=requesting_practice_name,
                ods_code=requesting_ods_code,
                metrics=[
                    MonthlyMetricsPresentation(
                        year=2019,
                        month=12,
                        requested_transfers=RequestedTransferMetrics(
                            requested_count=5,
                            received_count=5,
                            integrated_within_3_days_count=2,
                            integrated_within_8_days_count=0,
                            received_percent_of_requested=100.0,
                            integrated_within_3_days_percent_of_received=40.0,
                            integrated_within_8_days_percent_of_received=0.0,
                            not_integrated_within_8_days_total=3,
                            not_integrated_within_8_days_percent_of_received=60.0,
                            failures_total_count=0,
                            failures_total_percent_of_requested=0.0,
                        ),
                    )
                ],
            )
        ],
        ccgs=ccg_list,
    )

    actual = calculate_practice_metrics(
        transfers=transfers,
        organisation_metadata=organisation_metadata,
        reporting_window=reporting_window,
        observability_probe=mock_probe,
    )

    assert actual == expected
