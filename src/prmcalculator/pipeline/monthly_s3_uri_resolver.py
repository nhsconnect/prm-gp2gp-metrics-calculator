from typing import List, Optional

from prmcalculator.domain.monthly_reporting_window import YearMonth


class MonthlyPlatformMetricsS3UriResolver:

    _TRANSFER_DATA_VERSION = "v6"
    _DEFAULT_DATA_PLATFORM_METRICS_VERSION = "v7"
    _ORG_METADATA_VERSION = "v2"
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
        self._data_platform_metrics_version = self._DEFAULT_DATA_PLATFORM_METRICS_VERSION

    def ods_metadata(self, year_month: YearMonth) -> str:
        year, month = year_month
        s3_key = "/".join(
            [
                self._ods_bucket_name,
                self._ORG_METADATA_VERSION,
                f"{year}/{month}",
                self._ORG_METADATA_FILE_NAME,
            ]
        )
        return f"s3://{s3_key}"

    def practice_metrics(
        self, year_month: YearMonth, data_platform_metrics_version: Optional[str] = None
    ) -> str:
        year, month = year_month
        s3_key = "/".join(
            [
                self._data_platform_metrics_bucket,
                data_platform_metrics_version or self._data_platform_metrics_version,
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

    def _transfer_data_uri(self, year_month: YearMonth) -> str:
        year, month = year_month
        s3_file_name = f"{year}-{month}-{self._TRANSFER_DATA_FILE_NAME}"
        return "/".join(
            [
                self._transfer_data_bucket,
                self._TRANSFER_DATA_VERSION,
                f"{year}/{month}",
                s3_file_name,
            ]
        )

    def transfer_data(self, metric_months: List[YearMonth]) -> List[str]:
        return [f"s3://{self._transfer_data_uri(year_month)}" for year_month in metric_months]
