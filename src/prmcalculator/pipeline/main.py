from os import environ
import boto3
import logging
import pyarrow as pa
import polars as pl

from prmcalculator.domain.national.calculate_national_metrics_data import (
    calculate_national_metrics_data,
    NationalMetricsObservabilityProbe,
)
from prmcalculator.domain.supplier.count_outcomes_per_supplier_pathway import (
    count_outcomes_per_supplier_pathway,
)
from prmcalculator.domain.practice.calculate_practice_metrics import (
    calculate_practice_metrics,
    PracticeMetricsObservabilityProbe,
)
from prmcalculator.pipeline.config import PipelineConfig

from prmcalculator.pipeline.io import PlatformMetricsIO, PlatformMetricsS3UriResolver
from prmcalculator.utils.io.json_formatter import JsonFormatter
from prmcalculator.utils.io.s3 import S3DataManager
from prmcalculator.domain.datetime import MonthlyReportingWindow

logger = logging.getLogger("prmcalculator")


def _setup_logger():
    logger.setLevel(logging.INFO)
    formatter = JsonFormatter()
    handler = logging.StreamHandler()
    handler.setFormatter(formatter)
    logger.addHandler(handler)


class MetricsPipeline:
    def __init__(self, config: PipelineConfig):
        s3 = boto3.resource("s3", endpoint_url=config.s3_endpoint_url)
        s3_manager = S3DataManager(s3)

        self._reporting_window = MonthlyReportingWindow.prior_to(
            config.date_anchor, config.number_of_months
        )

        output_metadata = {
            "metrics-calculator-version": config.build_tag,
            "date-anchor": config.date_anchor.isoformat(),
            "number-of-months": str(config.number_of_months),
        }

        self._uris = PlatformMetricsS3UriResolver(
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

    def _read_transfer_table(self, months) -> pa.Table:
        transfer_table_s3_uri = self._uris.transfer_data(months)
        return self._io.read_transfers_as_table(transfer_table_s3_uri)

    def _calculate_national_metrics(self, transfers):
        return calculate_national_metrics_data(
            transfers=transfers,
            reporting_window=self._reporting_window,
            observability_probe=NationalMetricsObservabilityProbe(),
        )

    def _calculate_practice_metrics(self, transfers, ods_metadata):
        return calculate_practice_metrics(
            transfers=transfers,
            organisation_metadata=ods_metadata,
            reporting_window=self._reporting_window,
            observability_probe=PracticeMetricsObservabilityProbe(),
        )

    @staticmethod
    def _count_outcomes_per_supplier_pathway(transfer_table: pa.Table):
        transfers_frame = pl.from_arrow(transfer_table)
        return count_outcomes_per_supplier_pathway(transfers_frame)

    def _write_practice_metrics(self, practice_metrics, month):
        self._io.write_practice_metrics(
            practice_metrics_presentation_data=practice_metrics,
            s3_uri=self._uris.practice_metrics(month),
        )

    def _write_national_metrics(self, national_metrics, month):
        self._io.write_national_metrics(
            national_metrics_presentation_data=national_metrics,
            s3_uri=self._uris.national_metrics(month),
        )

    def _write_supplier_pathway_outcome_counts(
        self, supplier_pathway_outcome_counts: pl.DataFrame, month
    ):
        self._io.write_outcome_counts(
            dataframe=supplier_pathway_outcome_counts,
            s3_uri=self._uris.supplier_pathway_outcome_counts(month),
        )

    def run(self):
        date_anchor_month = self._reporting_window.date_anchor_month
        metric_months = self._reporting_window.metric_months
        last_month = self._reporting_window.last_metric_month
        ods_metadata = self._read_ods_metadata(date_anchor_month)
        transfers = self._read_transfer_data(metric_months)
        transfer_table = self._read_transfer_table([last_month])
        national_metrics = self._calculate_national_metrics(transfers)
        practice_metrics = self._calculate_practice_metrics(transfers, ods_metadata)
        supplier_pathway_outcome_counts = self._count_outcomes_per_supplier_pathway(transfer_table)
        self._write_national_metrics(national_metrics, last_month)
        self._write_practice_metrics(practice_metrics, last_month)
        self._write_supplier_pathway_outcome_counts(supplier_pathway_outcome_counts, last_month)


def main():
    _setup_logger()
    config = PipelineConfig.from_environment_variables(environ)
    pipeline = MetricsPipeline(config)
    pipeline.run()


if __name__ == "__main__":
    main()
