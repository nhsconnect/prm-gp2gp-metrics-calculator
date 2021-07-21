from os import environ
import boto3

from prmcalculator.pipeline.config import PipelineConfig
from prmcalculator.pipeline.core import calculate_practice_metrics_data
from prmcalculator.pipeline.io import PlatformMetricsIO
from prmcalculator.utils.io.s3 import S3DataManager
from prmcalculator.utils.reporting_window import MonthlyReportingWindow


def main():
    config = PipelineConfig.from_environment_variables(environ)

    s3 = boto3.resource("s3", endpoint_url=config.s3_endpoint_url)
    s3_manager = S3DataManager(s3)

    reporting_window = MonthlyReportingWindow.prior_to(config.date_anchor)

    metrics_io = PlatformMetricsIO(
        reporting_window=reporting_window,
        s3_data_manager=s3_manager,
        organisation_metadata_bucket=config.organisation_metadata_bucket,
        transfer_data_bucket=config.input_transfer_data_bucket,
        data_platform_metrics_bucket=config.output_metrics_bucket,
    )

    organisation_metadata = metrics_io.read_ods_metadata()

    transfers = metrics_io.read_transfer_data()

    practice_metrics_data = calculate_practice_metrics_data(
        transfers, organisation_metadata, reporting_window
    )

    metrics_io.write_practice_metrics(practice_metrics_data)
