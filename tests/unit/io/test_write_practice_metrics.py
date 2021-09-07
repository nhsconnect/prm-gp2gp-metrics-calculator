from datetime import datetime
from unittest.mock import Mock

from prmcalculator.domain.practice.calculate_practice_metrics_v5 import (
    PracticeMetricsPresentation,
)
from prmcalculator.domain.practice.construct_practice_summary_v5 import (
    PracticeSummary,
    MonthlyMetricsPresentation,
    RequesterMetrics,
    IntegratedPracticeMetricsPresentation,
    TransfersReceivedPresentation,
    AwaitingIntegration,
)

from prmcalculator.domain.ods_portal.organisation_metadata import CcgDetails
from prmcalculator.pipeline.io import PlatformMetricsIO
from prmcalculator.utils.reporting_window import MonthlyReportingWindow
from tests.builders.common import a_datetime, a_string

_DATE_ANCHOR_MONTH = 1
_DATE_ANCHOR_YEAR = 2021
_METRIC_MONTH = 12
_METRIC_YEAR = 2020

_PRACTICE_METRICS_OBJECT = PracticeMetricsPresentation(
    generated_on=datetime(_DATE_ANCHOR_YEAR, _DATE_ANCHOR_MONTH, 1),
    practices=[
        PracticeSummary(
            ods_code="A12345",
            name="A test GP practice",
            metrics=[
                MonthlyMetricsPresentation(
                    year=2021,
                    month=1,
                    requester=RequesterMetrics(
                        transfers_received=TransfersReceivedPresentation(
                            transfer_count=2,
                            awaiting_integration=AwaitingIntegration(percentage=50.0),
                            integrated=IntegratedPracticeMetricsPresentation(
                                within_3_days_percentage=50.0,
                                within_8_days_percentage=0.0,
                                beyond_8_days_percentage=0.0,
                            ),
                        ),
                    ),
                )
            ],
        )
    ],
    ccgs=[CcgDetails(name="A test CCG", ods_code="12A", practices=["A12345"])],
)

_PRACTICE_METRICS_DICT = {
    "generatedOn": datetime(_DATE_ANCHOR_YEAR, _DATE_ANCHOR_MONTH, 1),
    "practices": [
        {
            "odsCode": "A12345",
            "name": "A test GP practice",
            "metrics": [
                {
                    "year": 2021,
                    "month": 1,
                    "requester": {
                        "transfersReceived": {
                            "transferCount": 2,
                            "awaitingIntegration": {"percentage": 50.0},
                            "integrated": {
                                "within3DaysPercentage": 50.0,
                                "within8DaysPercentage": 0.0,
                                "beyond8DaysPercentage": 0.0,
                            },
                        },
                    },
                }
            ],
        },
    ],
    "ccgs": [{"name": "A test CCG", "odsCode": "12A", "practices": ["A12345"]}],
}


def test_given_practice_metrics_object_will_generate_json():
    s3_manager = Mock()
    date_anchor = a_datetime(year=_DATE_ANCHOR_YEAR, month=_DATE_ANCHOR_MONTH)
    reporting_window = MonthlyReportingWindow.prior_to(date_anchor=date_anchor, number_of_months=1)

    data_platform_metrics_bucket = a_string()

    metrics_io = PlatformMetricsIO(
        reporting_window=reporting_window,
        s3_data_manager=s3_manager,
        organisation_metadata_bucket=a_string(),
        transfer_data_bucket=a_string(),
        data_platform_metrics_bucket=data_platform_metrics_bucket,
    )

    metrics_io.write_practice_metrics(_PRACTICE_METRICS_OBJECT)

    expected_practice_metrics_dict = _PRACTICE_METRICS_DICT
    expected_s3_path_fragment = f"{data_platform_metrics_bucket}/v5/{_METRIC_YEAR}/{_METRIC_MONTH}"
    expected_s3_path = f"s3://{expected_s3_path_fragment}/practiceMetrics.json"

    s3_manager.write_json.assert_called_once_with(expected_s3_path, expected_practice_metrics_dict)
