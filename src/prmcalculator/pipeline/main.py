from os import environ
import boto3
import logging

from prmcalculator.domain.national.calculate_national_metrics_data import (
    calculate_national_metrics_data,
    NationalMetricsObservabilityProbe,
)
from prmcalculator.domain.practice.calculate_practice_metrics_v5 import (
    calculate_practice_metrics_v5,
    PracticeMetricsObservabilityProbe,
)

from prmcalculator.domain.practice.calculate_practice_metrics_v6 import calculate_practice_metrics
from prmcalculator.pipeline.config import PipelineConfig

from prmcalculator.pipeline.io import PlatformMetricsIO, PlatformMetricsS3UriResolver
from prmcalculator.utils.io.json_formatter import JsonFormatter
from prmcalculator.utils.io.s3 import S3DataManager
from prmcalculator.utils.reporting_window import MonthlyReportingWindow

logger = logging.getLogger("prmcalculator")


def _setup_logger():
    logger.setLevel(logging.INFO)
    formatter = JsonFormatter()
    handler = logging.StreamHandler()
    handler.setFormatter(formatter)
    logger.addHandler(handler)


def main():
    _setup_logger()

    config = PipelineConfig.from_environment_variables(environ)

    s3 = boto3.resource("s3", endpoint_url=config.s3_endpoint_url)
    s3_manager = S3DataManager(s3)

    reporting_window = MonthlyReportingWindow.prior_to(config.date_anchor, config.number_of_months)

    output_metadata = {"build-tag": config.build_tag, "date-anchor": config.date_anchor.isoformat()}

    s3_uri_resolver = PlatformMetricsS3UriResolver(
        ods_bucket=config.organisation_metadata_bucket,
        transfer_data_bucket=config.input_transfer_data_bucket,
        data_platform_metrics_bucket=config.output_metrics_bucket,
        output_v6_metrics=config.output_v6_metrics,
    )

    metrics_io = PlatformMetricsIO(
        s3_data_manager=s3_manager,
        output_metadata=output_metadata,
    )

    organisation_metadata_s3_uri = s3_uri_resolver.ods_metadata(
        year=reporting_window.date_anchor_year, month=reporting_window.date_anchor_month
    )
    organisation_metadata = metrics_io.read_ods_metadata(s3_uri=organisation_metadata_s3_uri)

    transfers_data_s3_uris = s3_uri_resolver.transfer_data(
        metric_months=reporting_window.metric_months
    )
    transfers = metrics_io.read_transfer_data(s3_uris=transfers_data_s3_uris)

    national_metrics_observability_probe = NationalMetricsObservabilityProbe()
    national_metrics_data = calculate_national_metrics_data(
        transfers=transfers,
        reporting_window=reporting_window,
        observability_probe=national_metrics_observability_probe,
    )

    practice_metrics_observability_probe = PracticeMetricsObservabilityProbe()

    practice_metrics_calculation = (
        calculate_practice_metrics if config.output_v6_metrics else calculate_practice_metrics_v5
    )
    practice_metrics_data = practice_metrics_calculation(
        transfers=transfers,
        organisation_metadata=organisation_metadata,
        reporting_window=reporting_window,
        observability_probe=practice_metrics_observability_probe,
    )

    practice_metrics_s3_uri = s3_uri_resolver.practice_metrics(
        year=reporting_window.metric_year, month=reporting_window.metric_month
    )
    metrics_io.write_practice_metrics(
        practice_metrics_presentation_data=practice_metrics_data, s3_uri=practice_metrics_s3_uri
    )

    national_metrics_s3_uri = s3_uri_resolver.national_metrics(
        year=reporting_window.metric_year, month=reporting_window.metric_month
    )
    metrics_io.write_national_metrics(
        national_metrics_presentation_data=national_metrics_data, s3_uri=national_metrics_s3_uri
    )


if __name__ == "__main__":
    main()
