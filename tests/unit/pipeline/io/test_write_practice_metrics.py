from datetime import datetime
from unittest.mock import Mock

from prmcalculator.domain.practice.calculate_practice_metrics import (
    PracticeMetricsPresentation,
)
from prmcalculator.domain.practice.construct_practice_summary import (
    PracticeSummary,
    MonthlyMetricsPresentation,
    RequestedTransferMetrics,
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
                    requested_transfers=RequestedTransferMetrics(
                        requested_count=9,
                        received_count=3,
                        integrated_count=2,
                        integrated_within_3_days_count=1,
                        integrated_within_8_days_count=0,
                        integrated_beyond_8_days_count=1,
                        awaiting_integration_count=1,
                        technical_failures_count=3,
                        unclassified_failure_count=4,
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
                    "requestedTransfers": {
                        "requestedCount": 9,
                        "receivedCount": 3,
                        "integratedCount": 2,
                        "integratedWithin3DaysCount": 1,
                        "integratedWithin8DaysCount": 0,
                        "integratedBeyond8DaysCount": 1,
                        "awaitingIntegrationCount": 1,
                        "technicalFailuresCount": 3,
                        "unclassifiedFailureCount": 4,
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
    s3_key = f"v6/{_METRIC_YEAR}/{_METRIC_MONTH}/practiceMetrics.json"
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
