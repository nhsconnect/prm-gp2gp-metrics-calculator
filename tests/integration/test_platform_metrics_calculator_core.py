from datetime import datetime, timedelta

from dateutil.tz import UTC
from freezegun import freeze_time

from prmcalculator.domain.practice.metrics_presentation import (
    IntegratedPracticeMetricsPresentation,
    RequesterMetrics,
    MonthlyMetrics,
    PracticeSummary,
    PracticeMetricsPresentation,
)
from prmcalculator.domain.ods_portal.organisation_metadata import (
    PracticeDetails,
    CcgDetails,
    OrganisationMetadata,
)
from prmcalculator.pipeline.core import calculate_practice_metrics_data

from prmcalculator.domain.gp2gp.transfer import (
    Transfer,
    TransferStatus,
    TransferOutcome,
    Practice,
)
from prmcalculator.utils.reporting_window import MonthlyReportingWindow


@freeze_time(datetime(year=2020, month=1, day=15, hour=23, second=42), tz_offset=0)
def test_calculates_correct_practice_metrics_given_a_successful_transfer():
    reporting_window = MonthlyReportingWindow(
        metric_month_start=datetime(2019, 12, 1, tzinfo=UTC),
        overflow_month_start=datetime(2020, 1, 1, tzinfo=UTC),
    )

    requesting_practice_name = "Test GP"
    requesting_ods_code = "A12345"
    requesting_practice = Practice(asid="343434343434", supplier="SystemOne")
    sending_practice = Practice(asid="111134343434", supplier="Unknown")
    conversation_id = "abcdefg_1234"
    ccg_ods_code = "23B"
    ccg_name = "Test CCG"

    transfers = [
        Transfer(
            conversation_id=conversation_id,
            sla_duration=timedelta(days=1, seconds=52707),
            requesting_practice=requesting_practice,
            sending_practice=sending_practice,
            outcome=TransferOutcome(failure_reason=None, status=TransferStatus.INTEGRATED_ON_TIME),
            date_requested=datetime(2019, 12, 30, 18, 2, 29, tzinfo=UTC),
            date_completed=datetime(2020, 1, 1, 8, 41, 48, tzinfo=UTC),
            sender_error_code=None,
            final_error_codes=[],
            intermediate_error_codes=[],
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
                    MonthlyMetrics(
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
