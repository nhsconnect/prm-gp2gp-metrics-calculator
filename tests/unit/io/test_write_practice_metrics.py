from datetime import datetime
from unittest import mock
from unittest.mock import Mock

from prmcalculator.domain.practice.metrics_presentation import (
    PracticeMetricsPresentation,
    PracticeSummary,
    MonthlyMetrics,
    RequesterMetrics,
    IntegratedPracticeMetricsPresentation,
)
from prmcalculator.domain.ods_portal.organisation_metadata import CcgDetails
from prmcalculator.pipeline.io import PlatformMetricsIO, logger
from prmcalculator.utils.reporting_window import MonthlyReportingWindow
from tests.builders.common import a_datetime, a_string

_OVERFLOW_MONTH = 1
_OVERFLOW_YEAR = 2021
_METRIC_MONTH = 12
_METRIC_YEAR = 2020

_PRACTICE_METRICS_OBJECT = PracticeMetricsPresentation(
    generated_on=datetime(_OVERFLOW_YEAR, _OVERFLOW_MONTH, 1),
    practices=[
        PracticeSummary(
            ods_code="A12345",
            name="A test GP practice",
            metrics=[
                MonthlyMetrics(
                    year=2021,
                    month=1,
                    requester=RequesterMetrics(
                        integrated=IntegratedPracticeMetricsPresentation(
                            transfer_count=1,
                            within_3_days_percentage=100.0,
                            within_8_days_percentage=0.0,
                            beyond_8_days_percentage=0.0,
                        ),
                    ),
                )
            ],
        )
    ],
    ccgs=[CcgDetails(name="A test CCG", ods_code="12A", practices=["A12345"])],
)

_PRACTICE_METRICS_DICT = {
    "generatedOn": datetime(_OVERFLOW_YEAR, _OVERFLOW_MONTH, 1),
    "practices": [
        {
            "odsCode": "A12345",
            "name": "A test GP practice",
            "metrics": [
                {
                    "year": 2021,
                    "month": 1,
                    "requester": {
                        "integrated": {
                            "transferCount": 1,
                            "within3DaysPercentage": 100.0,
                            "within8DaysPercentage": 0.0,
                            "beyond8DaysPercentage": 0.0,
                        }
                    },
                }
            ],
        },
    ],
    "ccgs": [{"name": "A test CCG", "odsCode": "12A", "practices": ["A12345"]}],
}


def test_given_practice_metrics_object_will_generate_json():
    s3_manager = Mock()
    date_anchor = a_datetime(year=_OVERFLOW_YEAR, month=_OVERFLOW_MONTH)
    reporting_window = MonthlyReportingWindow.prior_to(date_anchor)

    data_platform_metrics_bucket = a_string()

    metrics_io = PlatformMetricsIO(
        reporting_window=reporting_window,
        s3_data_manager=s3_manager,
        organisation_metadata_bucket=a_string(),
        transfer_data_bucket=a_string(),
        data_platform_metrics_bucket=data_platform_metrics_bucket,
    )

    metrics_io.write_practice_metrics(_PRACTICE_METRICS_OBJECT)

    expected_national_metrics_dict = _PRACTICE_METRICS_DICT
    expected_s3_path_fragment = f"{data_platform_metrics_bucket}/v4/{_METRIC_YEAR}/{_METRIC_MONTH}"
    expected_s3_path = f"s3://{expected_s3_path_fragment}/practiceMetrics.json"

    s3_manager.write_json.assert_called_once_with(expected_s3_path, expected_national_metrics_dict)


def test_will_log_successful_upload_message():
    s3_manager = Mock()
    date_anchor = a_datetime(year=_OVERFLOW_YEAR, month=_OVERFLOW_MONTH)
    reporting_window = MonthlyReportingWindow.prior_to(date_anchor)

    data_platform_metrics_bucket = a_string()

    with mock.patch.object(logger, "info") as mock_log_info:
        metrics_io = PlatformMetricsIO(
            reporting_window=reporting_window,
            s3_data_manager=s3_manager,
            organisation_metadata_bucket=a_string(),
            transfer_data_bucket=a_string(),
            data_platform_metrics_bucket=data_platform_metrics_bucket,
        )

        metrics_io.write_practice_metrics(_PRACTICE_METRICS_OBJECT)

        expected_s3_path = f"{data_platform_metrics_bucket}/v4/2020/12/practiceMetrics.json"
        mock_log_info.assert_called_once_with(
            f"Successfully calculated practice metrics and uploaded to s3://{expected_s3_path}"
        )
