from typing import List, Optional

import boto3

from prmcalculator.domain.gp2gp.transfer import Transfer
from prmcalculator.domain.monthly_reporting_window import MonthlyReportingWindow, YearMonth
from prmcalculator.domain.national.calculate_national_metrics_data import (
    NationalMetricsObservabilityProbe,
    calculate_national_metrics_data,
)
from prmcalculator.domain.ods_portal.organisation_metadata import OrganisationMetadata
from prmcalculator.domain.practice.calculate_practice_metrics import (
    PracticeMetricsObservabilityProbe,
    PracticeMetricsPresentation,
    calculate_practice_metrics,
)
from prmcalculator.pipeline.config import PipelineConfig
from prmcalculator.pipeline.io import PlatformMetricsIO
from prmcalculator.pipeline.monthly_s3_uri_resolver import MonthlyPlatformMetricsS3UriResolver
from prmcalculator.utils.io.s3 import S3DataManager


class MonthlyMetricsCalculator:
    def __init__(self, config: PipelineConfig):
        s3 = boto3.resource("s3", endpoint_url=config.s3_endpoint_url)
        s3_manager = S3DataManager(s3)

        self._reporting_window = MonthlyReportingWindow.prior_to(
            config.date_anchor, config.number_of_months
        )

        self._hide_slow_transferred_records_after_days = (
            config.hide_slow_transferred_records_after_days
        )

        output_metadata = {
            "metrics-calculator-version": config.build_tag,
            "date-anchor": config.date_anchor.isoformat(),
            "number-of-months": str(config.number_of_months),
        }

        self._uris = MonthlyPlatformMetricsS3UriResolver(
            ods_bucket=config.organisation_metadata_bucket,
            transfer_data_bucket=config.input_transfer_data_bucket,
            data_platform_metrics_bucket=config.output_metrics_bucket,
        )

        self._io = PlatformMetricsIO(
            s3_data_manager=s3_manager,
            output_metadata=output_metadata,
        )

    def _read_ods_metadata(self, month):
        org_metadata_uri = self._uris.ods_metadata(month)
        return self._io.read_ods_metadata(org_metadata_uri)

    def _read_transfer_data(self, months):
        transfers_data_s3_uris = self._uris.transfer_data(months)
        return self._io.read_transfers_as_dataclass(transfers_data_s3_uris)

    def _calculate_national_metrics(self, transfers):
        return calculate_national_metrics_data(
            transfers=transfers,
            reporting_window=self._reporting_window,
            observability_probe=NationalMetricsObservabilityProbe(),
        )

    def _calculate_practice_metrics(
        self,
        transfers: List[Transfer],
        ods_metadata: OrganisationMetadata,
        hide_slow_transferred_records_after_days: Optional[int],
    ):
        return calculate_practice_metrics(
            transfers=transfers,
            organisation_metadata=ods_metadata,
            reporting_window=self._reporting_window,
            observability_probe=PracticeMetricsObservabilityProbe(),
            hide_slow_transferred_records_after_days=hide_slow_transferred_records_after_days,
        )

    def _write_practice_metrics(
        self,
        practice_metrics: PracticeMetricsPresentation,
        year_month: YearMonth,
        data_platform_metrics_version: Optional[str] = None,
    ):
        self._io.write_practice_metrics(
            practice_metrics_presentation_data=practice_metrics,
            s3_uri=self._uris.practice_metrics(year_month, data_platform_metrics_version),
        )

    def _write_national_metrics(self, national_metrics, month):
        self._io.write_national_metrics(
            national_metrics_presentation_data=national_metrics,
            s3_uri=self._uris.national_metrics(month),
        )

    def run(self):
        date_anchor_month = self._reporting_window.date_anchor_month
        metric_months = self._reporting_window.metric_months
        last_month = self._reporting_window.last_metric_month
        ods_metadata = self._read_ods_metadata(date_anchor_month)
        transfers = self._read_transfer_data(metric_months)
        national_metrics = self._calculate_national_metrics(transfers)
        practice_metrics_deprecated = self._calculate_practice_metrics(
            transfers, ods_metadata, hide_slow_transferred_records_after_days=None
        )
        practice_metrics = self._calculate_practice_metrics(
            transfers,
            ods_metadata,
            hide_slow_transferred_records_after_days=self._hide_slow_transferred_records_after_days,
        )
        self._write_national_metrics(national_metrics, last_month)
        self._write_practice_metrics(
            practice_metrics_deprecated, last_month, data_platform_metrics_version="v6"
        )
        self._write_practice_metrics(practice_metrics, last_month)
