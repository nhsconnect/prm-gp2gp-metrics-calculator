from datetime import datetime, timedelta
from unittest.mock import Mock

from dateutil.tz import UTC
from freezegun import freeze_time

from prmcalculator.domain.gp2gp.transfer import Practice
from prmcalculator.domain.ods_portal.organisation_metadata import (
    PracticeDetails,
    CcgDetails,
    OrganisationMetadata,
)
from prmcalculator.domain.practice.calculate_practice_metrics import (
    calculate_practice_metrics,
    PracticeMetricsPresentation,
)
from prmcalculator.domain.practice.construct_practice_summary import (
    MonthlyMetricsPresentation,
    PracticeSummary,
    RequestedTransferMetrics,
)

from prmcalculator.domain.datetime import MonthlyReportingWindow
from tests.builders.common import a_datetime
from tests.builders.gp2gp import (
    a_transfer_that_was_never_integrated,
    a_transfer_integrated_within_3_days,
)


@freeze_time(datetime(year=2020, month=1, day=15, hour=23, second=42), tz_offset=0)
def test_calculates_correct_practice_metrics_given_transfers():
    mock_probe = Mock()
    metric_month_start = a_datetime(year=2019, month=12, day=1)

    reporting_window = MonthlyReportingWindow(
        date_anchor_month_start=a_datetime(year=2020, month=1, day=1),
        metric_monthly_datetimes=[metric_month_start],
    )

    requesting_practice_name = "Test GP"
    requesting_ods_code = "A12345"
    requesting_practice = Practice(asid="343434343434", supplier="SystemOne")
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
                name=requesting_practice_name,
                ods_code=requesting_ods_code,
                metrics=[
                    MonthlyMetricsPresentation(
                        year=2019,
                        month=12,
                        requested_transfers=RequestedTransferMetrics(
                            requested_count=2,
                            received_count=2,
                            integrated_count=1,
                            integrated_within_3_days_count=1,
                            integrated_within_8_days_count=0,
                            integrated_beyond_8_days_count=0,
                            awaiting_integration_count=1,
                            technical_failures_count=0,
                            unclassified_failure_count=0,
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

    reporting_window = MonthlyReportingWindow(
        date_anchor_month_start=a_datetime(year=2020, month=1, day=1),
        metric_monthly_datetimes=[metric_month_start],
    )

    requesting_practice_name = "Test GP practice with no transfers"
    requesting_ods_code = "A4656"

    practice_list = [
        PracticeDetails(
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
                            integrated_count=0,
                            integrated_within_3_days_count=0,
                            integrated_within_8_days_count=0,
                            integrated_beyond_8_days_count=0,
                            awaiting_integration_count=0,
                            technical_failures_count=0,
                            unclassified_failure_count=0,
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

    reporting_window = MonthlyReportingWindow(
        date_anchor_month_start=a_datetime(),
        metric_monthly_datetimes=[a_datetime()],
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
def test_calculates_correct_practice_metrics_filtering_transfers_that_take_longer_than_a_day():
    mock_probe = Mock()
    metric_month_start = a_datetime(year=2019, month=12, day=1)

    reporting_window = MonthlyReportingWindow(
        date_anchor_month_start=a_datetime(year=2020, month=1, day=1),
        metric_monthly_datetimes=[metric_month_start],
    )

    requesting_practice_name = "Test GP"
    requesting_ods_code = "A12345"
    requesting_practice = Practice(asid="343434343434", supplier="SystemOne")
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
                name=requesting_practice_name,
                ods_code=requesting_ods_code,
                metrics=[
                    MonthlyMetricsPresentation(
                        year=2019,
                        month=12,
                        requested_transfers=RequestedTransferMetrics(
                            requested_count=2,
                            received_count=2,
                            integrated_count=1,
                            integrated_within_3_days_count=1,
                            integrated_within_8_days_count=0,
                            integrated_beyond_8_days_count=0,
                            awaiting_integration_count=1,
                            technical_failures_count=0,
                            unclassified_failure_count=0,
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
