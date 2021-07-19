from datetime import datetime

from dateutil.tz import tzutc

from prmcalculator.pipeline.config import (
    PipelineConfig,
    MissingEnvironmentVariable,
)


def test_reads_from_environment_variables_and_converts_to_required_format():
    environment = {
        "INPUT_TRANSFER_DATA_BUCKET": "input-transfer-data-bucket",
        "ORGANISATION_METADATA_BUCKET": "organisation-metadata-bucket",
        "OUTPUT_METRICS_BUCKET": "output-metrics-bucket",
        "DATE_ANCHOR": "2020-01-30T18:44:49Z",
    }

    expected_config = PipelineConfig(
        input_transfer_data_bucket="input-transfer-data-bucket",
        organisation_metadata_bucket="organisation-metadata-bucket",
        output_metrics_bucket="output-metrics-bucket",
        date_anchor=datetime(
            year=2020, month=1, day=30, hour=18, minute=44, second=49, tzinfo=tzutc()
        ),
    )

    actual_config = PipelineConfig.from_environment_variables(environment)

    assert actual_config == expected_config


def test_read_config_from_environment_when_optional_parameters_are_not_set():
    environment = {
        "INPUT_TRANSFER_DATA_BUCKET": "input-transfer-data-bucket",
        "ORGANISATION_METADATA_BUCKET": "organisation-metadata-bucket",
        "OUTPUT_METRICS_BUCKET": "output-metrics-bucket",
        "DATE_ANCHOR": "2020-01-30T18:44:49Z",
    }

    expected_config = PipelineConfig(
        input_transfer_data_bucket="input-transfer-data-bucket",
        organisation_metadata_bucket="organisation-metadata-bucket",
        output_metrics_bucket="output-metrics-bucket",
        date_anchor=datetime(
            year=2020, month=1, day=30, hour=18, minute=44, second=49, tzinfo=tzutc()
        ),
        s3_endpoint_url=None,
    )

    actual_config = PipelineConfig.from_environment_variables(environment)

    assert actual_config == expected_config


def test_error_from_environment_when_required_fields_are_not_set():
    environment = {
        "INPUT_TRANSFER_DATA_BUCKET": "input-transfer-data-bucket",
        "ORGANISATION_METADATA_BUCKET": "organisation-metadata-bucket",
    }

    try:
        PipelineConfig.from_environment_variables(environment)
    except MissingEnvironmentVariable as ex:
        assert (
            str(ex) == "Expected environment variable OUTPUT_METRICS_BUCKET was not set, exiting..."
        )
