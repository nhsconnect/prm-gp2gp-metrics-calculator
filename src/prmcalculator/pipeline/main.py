from os import environ
import boto3
import logging

from prmcalculator.pipeline.config import PipelineConfig
from prmcalculator.pipeline.core import (
    calculate_practice_metrics_data,
    calculate_national_metrics_data,
)
from prmcalculator.pipeline.io import PlatformMetricsIO
from prmcalculator.utils.io.s3 import S3DataManager
from prmcalculator.utils.reporting_window import MonthlyReportingWindow

logger = logging.getLogger(__name__)


def main():
    logging.basicConfig(level=logging.INFO)
    logger.info("Start to read environment variables from config")

    config = PipelineConfig.from_environment_variables(environ)

    s3 = boto3.resource("s3", endpoint_url=config.s3_endpoint_url)
    s3_manager = S3DataManager(s3)

    reporting_window = MonthlyReportingWindow.prior_to(config.date_anchor, config.number_of_months)
    logger.info(
        f"""Reporting Window: {reporting_window.metric_year}/{reporting_window.metric_month},
        date anchor: {reporting_window.date_anchor_year}/{reporting_window.date_anchor_month}"""
    )

    metrics_io = PlatformMetricsIO(
        reporting_window=reporting_window,
        s3_data_manager=s3_manager,
        organisation_metadata_bucket=config.organisation_metadata_bucket,
        transfer_data_bucket=config.input_transfer_data_bucket,
        data_platform_metrics_bucket=config.output_metrics_bucket,
    )

    logger.info(f"Reading from  s3://{config.organisation_metadata_bucket}")
    organisation_metadata = metrics_io.read_ods_metadata()

    logger.info(f"Reading from  s3://{config.input_transfer_data_bucket}")
    transfers = metrics_io.read_transfer_data()

    logger.info("Calculating practice metrics")
    practice_metrics_data = calculate_practice_metrics_data(
        transfers, organisation_metadata, reporting_window
    )

    logger.info("Calculating national metrics")
    national_metrics_data = calculate_national_metrics_data(
        transfers=transfers, reporting_window=reporting_window
    )

    logger.info(f"Attempting to write to S3 bucket {config.output_metrics_bucket}")
    metrics_io.write_practice_metrics(practice_metrics_data)
    metrics_io.write_national_metrics(national_metrics_data)


if __name__ == "__main__":
    main()
