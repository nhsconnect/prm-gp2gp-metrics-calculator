from datetime import datetime
from unittest.mock import Mock

from dateutil.tz import UTC

from prmcalculator.domain.national.construct_national_metrics_presentation import (
    NationalMetricsPresentation,
    NationalMetricMonthPresentation,
    OutcomeMetricsPresentation,
    PaperFallbackMetricsPresentation,
    ProcessFailureMetricsPresentation,
)
from prmcalculator.pipeline.io import PlatformMetricsIO
from prmcalculator.utils.reporting_window import MonthlyReportingWindow
from tests.builders.common import a_datetime, a_string

_DATE_ANCHOR_MONTH = 1
_DATE_ANCHOR_YEAR = 2021
_METRIC_MONTH = 12
_METRIC_YEAR = 2020

_NATIONAL_METRICS_OBJECT = NationalMetricsPresentation(
    generated_on=datetime(_DATE_ANCHOR_YEAR, _DATE_ANCHOR_MONTH, 1, tzinfo=UTC),
    metrics=[
        NationalMetricMonthPresentation(
            year=2019,
            month=12,
            transfer_count=6,
            integrated_on_time=OutcomeMetricsPresentation(
                transfer_count=4,
                transfer_percentage=44.44,
            ),
            paper_fallback=PaperFallbackMetricsPresentation(
                transfer_count=5,
                transfer_percentage=55.56,
                process_failure=ProcessFailureMetricsPresentation(
                    integrated_late=OutcomeMetricsPresentation(
                        transfer_count=1, transfer_percentage=11.11
                    ),
                    transferred_not_integrated=OutcomeMetricsPresentation(
                        transfer_count=1, transfer_percentage=11.11
                    ),
                ),
                technical_failure=OutcomeMetricsPresentation(
                    transfer_count=2, transfer_percentage=22.22
                ),
                unclassified_failure=OutcomeMetricsPresentation(
                    transfer_count=1, transfer_percentage=11.11
                ),
            ),
        )
    ],
)

_NATIONAL_METRICS_DICT = {
    "generatedOn": datetime(_DATE_ANCHOR_YEAR, _DATE_ANCHOR_MONTH, 1, tzinfo=UTC),
    "metrics": [
        {
            "year": 2019,
            "month": 12,
            "transferCount": 6,
            "integratedOnTime": {"transferCount": 4, "transferPercentage": 44.44},
            "paperFallback": {
                "transferCount": 5,
                "transferPercentage": 55.56,
                "processFailure": {
                    "integratedLate": {"transferCount": 1, "transferPercentage": 11.11},
                    "transferredNotIntegrated": {"transferCount": 1, "transferPercentage": 11.11},
                },
                "technicalFailure": {"transferCount": 2, "transferPercentage": 22.22},
                "unclassifiedFailure": {"transferCount": 1, "transferPercentage": 11.11},
            },
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
    expected_s3_path_fragment = f"{data_platform_metrics_bucket}/v5/{_METRIC_YEAR}/{_METRIC_MONTH}"
    expected_s3_path = f"s3://{expected_s3_path_fragment}/nationalMetrics.json"

    s3_manager.write_json.assert_called_once_with(
        object_uri=expected_s3_path, data=expected_national_metrics_dict, metadata={}
    )
