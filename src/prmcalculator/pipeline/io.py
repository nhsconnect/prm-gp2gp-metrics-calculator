from dataclasses import asdict

from prmcalculator.domain.practice.metrics_presentation import PracticeMetricsPresentation
from prmcalculator.domain.ods_portal.organisation_metadata import OrganisationMetadata
from prmcalculator.utils.io.dictionary import camelize_dict
from prmcalculator.utils.reporting_window import MonthlyReportingWindow
from prmcalculator.utils.io.s3 import S3DataManager


class PlatformMetricsIO:
    _ORG_METADATA_VERSION = "v2"
    _ORG_METADATA_FILE_NAME = "organisationMetadata.json"
    _DASHBOARD_DATA_VERSION = "v3"
    _PRACTICE_METRICS_FILE_NAME = "practiceMetrics.json"

    def __init__(
        self,
        *,
        reporting_window: MonthlyReportingWindow,
        s3_data_manager: S3DataManager,
        organisation_metadata_bucket: str,
        transfer_data_bucket: str,
        data_platform_metrics_bucket: str,
    ):
        self._window = reporting_window
        self._s3_manager = s3_data_manager
        self._org_metadata_bucket_name = organisation_metadata_bucket
        self._transfer_data_bucket = transfer_data_bucket
        self._data_platform_metrics_bucket = data_platform_metrics_bucket

    def _data_platform_metrics_bucket_s3_path(self, file_name: str) -> str:
        return "/".join(
            [
                self._data_platform_metrics_bucket,
                self._DASHBOARD_DATA_VERSION,
                self._metric_month_path_fragment(),
                file_name,
            ]
        )

    @staticmethod
    def _create_platform_json_object(platform_data) -> dict:
        content_dict = asdict(platform_data)
        return camelize_dict(content_dict)

    def _metric_month_path_fragment(self) -> str:
        return f"{self._window.metric_year}/{self._window.metric_month}"

    def _overflow_month_path_fragment(self) -> str:
        return f"{self._window.overflow_year}/{self._window.overflow_month}"

    def read_ods_metadata(self) -> OrganisationMetadata:
        ods_metadata_s3_path = "/".join(
            [
                self._org_metadata_bucket_name,
                self._ORG_METADATA_VERSION,
                self._overflow_month_path_fragment(),
                self._ORG_METADATA_FILE_NAME,
            ]
        )

        ods_metadata_dict = self._s3_manager.read_json(f"s3://{ods_metadata_s3_path}")
        return OrganisationMetadata.from_dict(ods_metadata_dict)

    def write_practice_metrics(self, practice_metrics: PracticeMetricsPresentation):
        practice_metrics_path = self._data_platform_metrics_bucket_s3_path(
            self._PRACTICE_METRICS_FILE_NAME
        )
        self._s3_manager.write_json(
            f"s3://{practice_metrics_path}",
            self._create_platform_json_object(practice_metrics),
        )
