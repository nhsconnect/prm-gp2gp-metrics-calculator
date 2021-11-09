from dataclasses import asdict
from typing import List, Dict
import logging
import pyarrow as pa
import polars as pl

from prmcalculator.domain.gp2gp.transfer import Transfer, convert_table_to_transfers
from prmcalculator.domain.national.construct_national_metrics_presentation import (
    NationalMetricsPresentation,
)

from prmcalculator.domain.ods_portal.organisation_metadata import OrganisationMetadata
from prmcalculator.utils.io.dictionary import camelize_dict
from prmcalculator.domain.datetime import YearMonth
from prmcalculator.utils.io.s3 import S3DataManager

logger = logging.getLogger(__name__)

_TRANSFER_DATA_VERSION = "v5"
_ORG_METADATA_VERSION = "v2"
_DEFAULT_DATA_PLATFORM_METRICS_VERSION = "v6"


class PlatformMetricsS3UriResolver:
    _ORG_METADATA_FILE_NAME = "organisationMetadata.json"
    _PRACTICE_METRICS_FILE_NAME = "practiceMetrics.json"
    _NATIONAL_METRICS_FILE_NAME = "nationalMetrics.json"
    _SUPPLIER_PATHWAY_OUTCOME_COUNTS_FILE_NAME = "supplier_pathway_outcome_counts.csv"
    _TRANSFER_DATA_FILE_NAME = "transfers.parquet"

    def __init__(
        self,
        ods_bucket: str,
        transfer_data_bucket: str,
        data_platform_metrics_bucket: str,
    ):
        self._ods_bucket_name = ods_bucket
        self._transfer_data_bucket = transfer_data_bucket
        self._data_platform_metrics_bucket = data_platform_metrics_bucket
        self._data_platform_metrics_version = _DEFAULT_DATA_PLATFORM_METRICS_VERSION

    def ods_metadata(self, year_month: YearMonth) -> str:
        year, month = year_month
        s3_key = "/".join(
            [
                self._ods_bucket_name,
                _ORG_METADATA_VERSION,
                f"{year}/{month}",
                self._ORG_METADATA_FILE_NAME,
            ]
        )
        return f"s3://{s3_key}"

    def practice_metrics(self, year_month: YearMonth) -> str:
        year, month = year_month
        s3_key = "/".join(
            [
                self._data_platform_metrics_bucket,
                self._data_platform_metrics_version,
                f"{year}/{month}",
                f"{year}-{month}-{self._PRACTICE_METRICS_FILE_NAME}",
            ]
        )
        return f"s3://{s3_key}"

    def national_metrics(self, year_month: YearMonth) -> str:
        year, month = year_month
        s3_key = "/".join(
            [
                self._data_platform_metrics_bucket,
                self._data_platform_metrics_version,
                f"{year}/{month}",
                f"{year}-{month}-{self._NATIONAL_METRICS_FILE_NAME}",
            ]
        )
        return f"s3://{s3_key}"

    def supplier_pathway_outcome_counts(self, year_month: YearMonth) -> str:
        year, month = year_month
        s3_key = "/".join(
            [
                self._data_platform_metrics_bucket,
                self._data_platform_metrics_version,
                f"{year}/{month}",
                f"{year}-{month}-{self._SUPPLIER_PATHWAY_OUTCOME_COUNTS_FILE_NAME}",
            ]
        )
        return f"s3://{s3_key}"

    def _transfer_data_uri(self, year_month: YearMonth) -> str:
        year, month = year_month
        s3_file_name = f"{year}-{month}-{self._TRANSFER_DATA_FILE_NAME}"
        return "/".join(
            [
                self._transfer_data_bucket,
                _TRANSFER_DATA_VERSION,
                f"{year}/{month}",
                s3_file_name,
            ]
        )

    def transfer_data(self, metric_months: List[YearMonth]) -> List[str]:
        return [f"s3://{self._transfer_data_uri(year_month)}" for year_month in metric_months]


class PlatformMetricsIO:
    def __init__(
        self,
        s3_data_manager: S3DataManager,
        output_metadata: Dict[str, str],
    ):
        self._s3_manager = s3_data_manager
        self._output_metadata = output_metadata

    @staticmethod
    def _create_platform_json_object(platform_data) -> dict:
        content_dict = asdict(platform_data)
        return camelize_dict(content_dict)

    def read_ods_metadata(self, s3_uri: str) -> OrganisationMetadata:
        ods_metadata_dict = self._s3_manager.read_json(s3_uri)
        return OrganisationMetadata.from_dict(ods_metadata_dict)

    def read_transfers_as_dataclass(self, s3_uris: List[str]) -> List[Transfer]:
        transfer_table = self.read_transfers_as_table(s3_uris)
        return convert_table_to_transfers(transfer_table)

    def read_transfers_as_table(self, s3_uris: List[str]) -> pa.Table:
        return pa.concat_tables(
            [self._s3_manager.read_parquet(s3_path) for s3_path in s3_uris],
        )

    def write_national_metrics(
        self, national_metrics_presentation_data: NationalMetricsPresentation, s3_uri: str
    ):
        self._s3_manager.write_json(
            object_uri=s3_uri,
            data=self._create_platform_json_object(national_metrics_presentation_data),
            metadata=self._output_metadata,
        )

    def write_practice_metrics(self, practice_metrics_presentation_data, s3_uri: str):
        self._s3_manager.write_json(
            object_uri=s3_uri,
            data=self._create_platform_json_object(practice_metrics_presentation_data),
            metadata=self._output_metadata,
        )

    def write_outcome_counts(self, dataframe: pl.DataFrame, s3_uri: str):
        self._s3_manager.write_dataframe_to_csv(
            object_uri=s3_uri, dataframe=dataframe, metadata=self._output_metadata
        )
