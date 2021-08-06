from datetime import datetime
from unittest import mock
from unittest.mock import Mock

from prmcalculator.domain.national.metrics_presentation import (
    NationalMetricsPresentation,
    MonthlyNationalMetrics,
    FailedMetrics,
    PendingMetrics,
    PaperFallbackMetrics,
    IntegratedMetricsPresentation,
)
from prmcalculator.pipeline.io import PlatformMetricsIO, logger
from prmcalculator.utils.reporting_window import MonthlyReportingWindow
from tests.builders.common import a_datetime, a_string

_DATE_ANCHOR_MONTH = 1
_DATE_ANCHOR_YEAR = 2021
_METRIC_MONTH = 12
_METRIC_YEAR = 2020

_NATIONAL_METRICS_OBJECT = NationalMetricsPresentation(
    generated_on=datetime(_DATE_ANCHOR_YEAR, _DATE_ANCHOR_MONTH, 1),
    metrics=[
        MonthlyNationalMetrics(
            transfer_count=6,
            integrated=IntegratedMetricsPresentation(
                transfer_percentage=83.33,
                transfer_count=5,
                within_3_days=2,
                within_8_days=2,
                beyond_8_days=1,
            ),
            failed=FailedMetrics(transfer_count=1, transfer_percentage=16.67),
            pending=PendingMetrics(transfer_count=0, transfer_percentage=0.0),
            paper_fallback=PaperFallbackMetrics(transfer_count=2, transfer_percentage=33.33),
            year=2019,
            month=12,
        )
    ],
)

_NATIONAL_METRICS_DICT = {
    "generatedOn": datetime(_DATE_ANCHOR_YEAR, _DATE_ANCHOR_MONTH, 1),
    "metrics": [
        {
            "transferCount": 6,
            "integrated": {
                "transferPercentage": 83.33,
                "transferCount": 5,
                "within3Days": 2,
                "within8Days": 2,
                "beyond8Days": 1,
            },
            "failed": {"transferCount": 1, "transferPercentage": 16.67},
            "pending": {"transferCount": 0, "transferPercentage": 0.0},
            "paperFallback": {"transferCount": 2, "transferPercentage": 33.33},
            "year": 2019,
            "month": 12,
        }
    ],
}


def test_given_national_metrics_object_will_generate_json():
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

    metrics_io.write_national_metrics(_NATIONAL_METRICS_OBJECT)

    expected_national_metrics_dict = _NATIONAL_METRICS_DICT
    expected_s3_path_fragment = f"{data_platform_metrics_bucket}/v4/{_METRIC_YEAR}/{_METRIC_MONTH}"
    expected_s3_path = f"s3://{expected_s3_path_fragment}/nationalMetrics.json"

    s3_manager.write_json.assert_called_once_with(expected_s3_path, expected_national_metrics_dict)


def test_will_log_successful_upload_message():
    s3_manager = Mock()
    date_anchor = a_datetime(year=_DATE_ANCHOR_YEAR, month=_DATE_ANCHOR_MONTH)
    reporting_window = MonthlyReportingWindow.prior_to(date_anchor=date_anchor, number_of_months=1)

    data_platform_metrics_bucket = a_string()

    with mock.patch.object(logger, "info") as mock_log_info:
        metrics_io = PlatformMetricsIO(
            reporting_window=reporting_window,
            s3_data_manager=s3_manager,
            organisation_metadata_bucket=a_string(),
            transfer_data_bucket=a_string(),
            data_platform_metrics_bucket=data_platform_metrics_bucket,
        )

        metrics_io.write_national_metrics(_NATIONAL_METRICS_OBJECT)

        expected_s3_path = f"{data_platform_metrics_bucket}/v4/2020/12/nationalMetrics.json"
        mock_log_info.assert_called_once_with(
            f"Successfully calculated national metrics and uploaded to s3://{expected_s3_path}"
        )
