from dataclasses import asdict
from typing import List, Optional, Dict
import logging
import pyarrow as pa

from prmcalculator.domain.gp2gp.transfer import Transfer, convert_table_to_transfers
from prmcalculator.domain.national.construct_national_metrics_presentation import (
    NationalMetricsPresentation,
)

from prmcalculator.domain.ods_portal.organisation_metadata import OrganisationMetadata
from prmcalculator.utils.io.dictionary import camelize_dict
from prmcalculator.utils.reporting_window import MonthlyReportingWindow
from prmcalculator.utils.io.s3 import S3DataManager

logger = logging.getLogger(__name__)

_TRANSFER_DATA_VERSION = "v4"
_ORG_METADATA_VERSION = "v2"
_DEFAULT_DATA_PLATFORM_METRICS_VERSION = "v5"
_DATA_PLATFORM_METRICS_V6 = "v6"


class PlatformMetricsS3UriResolver:
    _ORG_METADATA_FILE_NAME = "organisationMetadata.json"
    _PRACTICE_METRICS_FILE_NAME = "practiceMetrics.json"

    def __init__(
        self,
        ods_bucket: str,
        data_platform_metrics_bucket: str,
        output_v6_metrics: Optional[bool] = False,
    ):
        self._ods_bucket_name = ods_bucket
        self.data_platform_metrics_bucket = data_platform_metrics_bucket
        self._output_v6_metrics = output_v6_metrics

    def ods_metadata(self, year: int, month: int):
        s3_key = "/".join(
            [
                self._ods_bucket_name,
                _ORG_METADATA_VERSION,
                f"{year}/{month}",
                self._ORG_METADATA_FILE_NAME,
            ]
        )
        return f"s3://{s3_key}"

    def practice_metrics(self, year: int, month: int):
        version = (
            _DATA_PLATFORM_METRICS_V6
            if self._output_v6_metrics
            else _DEFAULT_DATA_PLATFORM_METRICS_VERSION
        )
        s3_key = "/".join(
            [
                self.data_platform_metrics_bucket,
                version,
                f"{year}/{month}",
                self._PRACTICE_METRICS_FILE_NAME,
            ]
        )
        return f"s3://{s3_key}"


class PlatformMetricsIO:
    _ORG_METADATA_FILE_NAME = "organisationMetadata.json"
    _PRACTICE_METRICS_FILE_NAME = "practiceMetrics.json"
    _NATIONAL_METRICS_FILE_NAME = "nationalMetrics.json"
    _TRANSFER_DATA_FILE_NAME = "transfers.parquet"

    def __init__(
        self,
        *,
        reporting_window: MonthlyReportingWindow,
        s3_data_manager: S3DataManager,
        organisation_metadata_bucket: str,
        transfer_data_bucket: str,
        data_platform_metrics_bucket: str,
        data_platform_metrics_version: Optional[str] = None,
        output_metadata: Dict[str, str],
    ):
        self._window = reporting_window
        self._s3_manager = s3_data_manager
        self._org_metadata_bucket_name = organisation_metadata_bucket
        self._transfer_data_bucket = transfer_data_bucket
        self._data_platform_metrics_bucket = data_platform_metrics_bucket
        self._data_platform_metrics_version = (
            data_platform_metrics_version or _DEFAULT_DATA_PLATFORM_METRICS_VERSION
        )
        self._output_metadata = output_metadata

    def _data_platform_metrics_bucket_s3_path(self, file_name: str) -> str:
        return "/".join(
            [
                self._data_platform_metrics_bucket,
                self._data_platform_metrics_version,
                self._metric_month_path_fragment(),
                file_name,
            ]
        )

    def _transfer_data_bucket_s3_path(self, year: int, month: int) -> str:
        return "/".join(
            [
                self._transfer_data_bucket,
                _TRANSFER_DATA_VERSION,
                f"{year}/{month}",
                self._TRANSFER_DATA_FILE_NAME,
            ]
        )

    @staticmethod
    def _create_platform_json_object(platform_data) -> dict:
        content_dict = asdict(platform_data)
        return camelize_dict(content_dict)

    def _metric_month_path_fragment(self) -> str:
        return f"{self._window.metric_year}/{self._window.metric_month}"

    def _date_anchor_month_path_fragment(self) -> str:
        return f"{self._window.date_anchor_year}/{self._window.date_anchor_month}"

    def read_ods_metadata(self) -> OrganisationMetadata:
        ods_metadata_s3_path = "/".join(
            [
                self._org_metadata_bucket_name,
                _ORG_METADATA_VERSION,
                self._date_anchor_month_path_fragment(),
                self._ORG_METADATA_FILE_NAME,
            ]
        )

        ods_metadata_dict = self._s3_manager.read_json(f"s3://{ods_metadata_s3_path}")
        return OrganisationMetadata.from_dict(ods_metadata_dict)

    def write_national_metrics(
        self, national_metrics_presentation_data: NationalMetricsPresentation
    ):
        national_metrics_path = self._data_platform_metrics_bucket_s3_path(
            self._NATIONAL_METRICS_FILE_NAME
        )
        self._s3_manager.write_json(
            object_uri=f"s3://{national_metrics_path}",
            data=self._create_platform_json_object(national_metrics_presentation_data),
            metadata=self._output_metadata,
        )

    def write_practice_metrics(self, practice_metrics):
        practice_metrics_path = self._data_platform_metrics_bucket_s3_path(
            self._PRACTICE_METRICS_FILE_NAME
        )
        self._s3_manager.write_json(
            object_uri=f"s3://{practice_metrics_path}",
            data=self._create_platform_json_object(practice_metrics),
            metadata=self._output_metadata,
        )

    def read_transfer_data(self) -> List[Transfer]:
        transfer_data_s3_paths = [
            self._transfer_data_bucket_s3_path(year, month)
            for (year, month) in self._window.metric_months
        ]
        transfer_table = pa.concat_tables(
            [
                self._s3_manager.read_parquet(f"s3://{s3_path}")
                for s3_path in transfer_data_s3_paths
            ],
            promote=True,
        )

        return convert_table_to_transfers(transfer_table)
