from datetime import datetime, timedelta

from dateutil.tz import UTC
from freezegun import freeze_time

from prmcalculator.domain.gp2gp.transfer import (
    Transfer,
    TransferStatus,
    TransferOutcome,
    Practice,
)
from prmcalculator.domain.ods_portal.organisation_metadata import (
    PracticeDetails,
    CcgDetails,
    OrganisationMetadata,
)
from prmcalculator.domain.practice.deprecated.calculate_practice_metrics_data_deprecated import (
    calculate_practice_metrics_data_deprecated,
)
from prmcalculator.domain.practice.deprecated.metrics_presentation_deprecated import (
    IntegratedPracticeMetricsPresentationDeprecated,
    RequesterMetricsDeprecated,
    MonthlyMetricsPresentationDeprecated,
    PracticeSummaryDeprecated,
    PracticeMetricsPresentationDeprecated,
)
from prmcalculator.utils.reporting_window import MonthlyReportingWindow
from tests.builders.common import a_datetime


@freeze_time(datetime(year=2020, month=1, day=15, hour=23, second=42), tz_offset=0)
def test_calculates_correct_practice_metrics_given_a_successful_transfer():
    metric_month_start = a_datetime(year=2019, month=12, day=1)

    reporting_window = MonthlyReportingWindow(
        date_anchor_month_start=a_datetime(year=2020, month=1, day=1),
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

    expected = PracticeMetricsPresentationDeprecated(
        generated_on=datetime(year=2020, month=1, day=15, hour=23, second=42, tzinfo=UTC),
        practices=[
            PracticeSummaryDeprecated(
                ods_code=requesting_ods_code,
                name=requesting_practice_name,
                metrics=[
                    MonthlyMetricsPresentationDeprecated(
                        year=2019,
                        month=12,
                        requester=RequesterMetricsDeprecated(
                            integrated=IntegratedPracticeMetricsPresentationDeprecated(
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

    actual = calculate_practice_metrics_data_deprecated(
        transfers, organisation_metadata, reporting_window
    )

    assert actual == expected
