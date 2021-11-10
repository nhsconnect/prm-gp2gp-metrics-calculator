from datetime import datetime

import pytest
from dateutil.tz import tzutc

from prmcalculator.pipeline.config import (
    PipelineConfig,
    MissingEnvironmentVariable,
)


def test_reads_from_environment_variables_and_converts_to_required_format():
    build_tag = "61ad1e1c"
    environment = {
        "INPUT_TRANSFER_DATA_BUCKET": "input-transfer-data-bucket",
        "ORGANISATION_METADATA_BUCKET": "metadata-bucket",
        "OUTPUT_METRICS_BUCKET": "output-metrics-bucket",
        "NUMBER_OF_MONTHS": "3",
        "DATE_ANCHOR": "2020-01-30T18:44:49Z",
        "S3_ENDPOINT_URL": "a_url",
        "BUILD_TAG": build_tag,
        "HIDE_SLOW_TRANSFERRED_RECORDS_AFTER_DAYS": "3",
    }

    expected_config = PipelineConfig(
        input_transfer_data_bucket="input-transfer-data-bucket",
        organisation_metadata_bucket="metadata-bucket",
        output_metrics_bucket="output-metrics-bucket",
        number_of_months=3,
        date_anchor=datetime(
            year=2020, month=1, day=30, hour=18, minute=44, second=49, tzinfo=tzutc()
        ),
        s3_endpoint_url="a_url",
        build_tag=build_tag,
        hide_slow_transferred_records_after_days=3,
    )

    actual_config = PipelineConfig.from_environment_variables(environment)

    assert actual_config == expected_config


def test_read_config_from_environment_when_optional_parameters_are_not_set():
    build_tag = "61ad1e1c"
    environment = {
        "INPUT_TRANSFER_DATA_BUCKET": "input-transfer-data-bucket",
        "ORGANISATION_METADATA_BUCKET": "metadata-bucket",
        "OUTPUT_METRICS_BUCKET": "output-metrics-bucket",
        "DATE_ANCHOR": "2020-01-30T18:44:49Z",
        "BUILD_TAG": build_tag,
    }

    expected_config = PipelineConfig(
        input_transfer_data_bucket="input-transfer-data-bucket",
        organisation_metadata_bucket="metadata-bucket",
        output_metrics_bucket="output-metrics-bucket",
        number_of_months=1,
        date_anchor=datetime(
            year=2020, month=1, day=30, hour=18, minute=44, second=49, tzinfo=tzutc()
        ),
        s3_endpoint_url=None,
        build_tag=build_tag,
        hide_slow_transferred_records_after_days=1,
    )

    actual_config = PipelineConfig.from_environment_variables(environment)

    assert actual_config == expected_config


def test_error_from_environment_when_required_fields_are_not_set():
    environment = {
        "INPUT_TRANSFER_DATA_BUCKET": "input-transfer-data-bucket",
        "ORGANISATION_METADATA_BUCKET": "organisation-metadata-bucket",
    }

    with pytest.raises(MissingEnvironmentVariable) as e:
        PipelineConfig.from_environment_variables(environment)
        assert str(e) == "Expected environment variable BUILD_TAG was not set, exiting..."
