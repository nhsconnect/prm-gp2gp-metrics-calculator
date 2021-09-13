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
from tests.builders.common import a_string

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

    data_platform_metrics_bucket = a_string()
    s3_key = f"v5/{_METRIC_YEAR}/{_METRIC_MONTH}/practiceMetrics.json"
    s3_uri = f"s3://{data_platform_metrics_bucket}/{s3_key}"

    output_metadata = {"metadata-field": "metadata_value"}
    metrics_io = PlatformMetricsIO(
        s3_data_manager=s3_manager,
        output_metadata=output_metadata,
    )

    metrics_io.write_practice_metrics(
        practice_metrics_presentation_data=_PRACTICE_METRICS_OBJECT, s3_uri=s3_uri
    )

    expected_practice_metrics_dict = _PRACTICE_METRICS_DICT

    s3_manager.write_json.assert_called_once_with(
        object_uri=s3_uri, data=expected_practice_metrics_dict, metadata=output_metadata
    )


def test_given_data_platform_metrics_version_will_override_default():
    s3_manager = Mock()

    data_platform_metrics_bucket = a_string()
    data_platform_metrics_version = "v102"
    s3_uri = (
        f"s3://{data_platform_metrics_bucket}"
        f"/{data_platform_metrics_version}"
        f"/{_METRIC_YEAR}/{_METRIC_MONTH}/practiceMetrics.json"
    )

    metrics_io = PlatformMetricsIO(
        s3_data_manager=s3_manager,
        output_metadata={},
    )

    metrics_io.write_practice_metrics(
        practice_metrics_presentation_data=_PRACTICE_METRICS_OBJECT, s3_uri=s3_uri
    )

    expected_practice_metrics_dict = _PRACTICE_METRICS_DICT

    s3_manager.write_json.assert_called_once_with(
        object_uri=s3_uri, data=expected_practice_metrics_dict, metadata={}
    )
