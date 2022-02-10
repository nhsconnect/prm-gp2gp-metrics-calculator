import json
import logging
from datetime import datetime
from io import BytesIO
from os import environ
from threading import Thread

import boto3
import pyarrow as pa
import pytest
from botocore.config import Config
from moto.server import DomainDispatcherApplication, create_backend_app
from pyarrow._s3fs import S3FileSystem
from pyarrow.parquet import write_table
from werkzeug.serving import make_server

from prmcalculator.pipeline.main import main
from prmcalculator.utils.add_leading_zero import add_leading_zero
from tests.builders.common import a_string

logger = logging.getLogger(__name__)


class ThreadedServer:
    def __init__(self, server):
        self._server = server
        self._thread = Thread(target=server.serve_forever)

    def start(self):
        self._thread.start()

    def stop(self):
        self._server.shutdown()
        self._thread.join()


def _read_json(path):
    return json.loads(path.read_text())


def _parse_dates(items):
    return [None if item is None else datetime.fromisoformat(item) for item in items]


def _read_parquet_columns_json(path):
    datetime_columns = ["date_requested", "last_sender_message_timestamp"]
    return {
        column_name: _parse_dates(values) if column_name in datetime_columns else values
        for column_name, values in _read_json(path).items()
    }


def _read_s3_json(bucket, key):
    f = BytesIO()
    bucket.download_fileobj(key, f)
    f.seek(0)
    return json.loads(f.read().decode("utf-8"))


def _read_s3_metadata(bucket, key):
    return bucket.Object(key).get()["Metadata"]


def _write_transfer_parquet(input_transfer_parquet_columns_json, s3_path: str):
    transfer_parquet_schema = pa.schema(
        [
            ("conversation_id", pa.string()),
            ("sla_duration", pa.uint64()),
            ("requesting_practice_asid", pa.string()),
            ("requesting_supplier", pa.string()),
            ("status", pa.string()),
            ("failure_reason", pa.string()),
            ("date_requested", pa.timestamp("us", tz="utc")),
            ("last_sender_message_timestamp", pa.timestamp("us", tz="utc")),
        ]
    )

    transfers_dictionary = _read_parquet_columns_json(input_transfer_parquet_columns_json)
    transfers_table = pa.table(data=transfers_dictionary, schema=transfer_parquet_schema)

    write_table(
        table=transfers_table,
        where=s3_path,
        filesystem=S3FileSystem(endpoint_override=fake_s3_url),
    )


def _build_fake_s3(host, port):
    app = DomainDispatcherApplication(create_backend_app, "s3")
    server = make_server(host, port, app)
    return ThreadedServer(server)


def _build_fake_s3_bucket(bucket_name: str, s3):
    s3_fake_bucket = s3.Bucket(bucket_name)
    s3_fake_bucket.create()
    return s3_fake_bucket


fake_s3_host = "127.0.0.1"
fake_s3_port = 8887
fake_s3_url = f"http://{fake_s3_host}:{fake_s3_port}"


def _get_s3_path(bucket_name, year, month, day):
    return f"{bucket_name}/v7/cutoff-14/{year}/{month}/{day}/{year}-{month}-{day}-transfers.parquet"


def _upload_template_transfer_data(
    datadir, input_transfer_bucket: str, year: int, data_month: int, time_range: range
):
    for data_day in time_range:
        day = add_leading_zero(data_day)
        month = add_leading_zero(data_month)

        _write_transfer_parquet(
            datadir / "inputs" / "template-transfers.json",
            _get_s3_path(input_transfer_bucket, year, month, day),
        )


def _override_transfer_data(
    datadir, input_transfer_bucket, year: int, data_month: int, data_day: int, input_folder: str
):
    day = add_leading_zero(data_day)
    month = add_leading_zero(data_month)

    _write_transfer_parquet(
        datadir / input_folder / f"{year}-{month}-{day}-transfers.json",
        _get_s3_path(input_transfer_bucket, year, month, day),
    )


@pytest.mark.filterwarnings("ignore:Conversion of")
def test_reads_daily_input_files_and_outputs_metrics_to_s3_hiding_slow_transfers(datadir):
    fake_s3_access_key = "testing"
    fake_s3_secret_key = "testing"
    fake_s3_region = "eu-west-2"
    s3_output_metrics_bucket_name = "output-metrics-bucket"
    s3_input_transfer_data_bucket_name = "input-transfer-data-bucket"
    s3_organisation_metadata_bucket_name = "organisation-metadata-bucket"
    build_tag = a_string(7)

    fake_s3 = _build_fake_s3(fake_s3_host, fake_s3_port)
    fake_s3.start()

    date_anchor = "2020-01-30T18:44:49Z"

    environ["AWS_ACCESS_KEY_ID"] = fake_s3_access_key
    environ["AWS_SECRET_ACCESS_KEY"] = fake_s3_secret_key
    environ["AWS_DEFAULT_REGION"] = fake_s3_region

    environ["INPUT_TRANSFER_DATA_BUCKET"] = s3_input_transfer_data_bucket_name
    environ["OUTPUT_METRICS_BUCKET"] = s3_output_metrics_bucket_name
    environ["ORGANISATION_METADATA_BUCKET"] = s3_organisation_metadata_bucket_name
    environ["NUMBER_OF_MONTHS"] = "2"
    environ["DATE_ANCHOR"] = date_anchor
    environ["S3_ENDPOINT_URL"] = fake_s3_url
    environ["BUILD_TAG"] = build_tag

    s3 = boto3.resource(
        "s3",
        endpoint_url=fake_s3_url,
        aws_access_key_id=fake_s3_access_key,
        aws_secret_access_key=fake_s3_secret_key,
        config=Config(signature_version="s3v4"),
        region_name=fake_s3_region,
    )

    output_metrics_bucket = _build_fake_s3_bucket(s3_output_metrics_bucket_name, s3)
    organisation_metadata_bucket = _build_fake_s3_bucket(s3_organisation_metadata_bucket_name, s3)

    organisation_metadata_file = str(datadir / "inputs" / "organisationMetadata.json")
    organisation_metadata_bucket.upload_file(
        organisation_metadata_file, "v2/2020/1/organisationMetadata.json"
    )

    input_transfer_bucket = _build_fake_s3_bucket(s3_input_transfer_data_bucket_name, s3)

    _upload_template_transfer_data(
        datadir,
        s3_input_transfer_data_bucket_name,
        year=2019,
        data_month=11,
        time_range=range(1, 31),
    )
    _override_transfer_data(
        datadir,
        s3_input_transfer_data_bucket_name,
        year=2019,
        data_month=11,
        data_day=1,
        input_folder="inputs/daily_hiding_slow_transfers",
    )

    _upload_template_transfer_data(
        datadir,
        s3_input_transfer_data_bucket_name,
        year=2019,
        data_month=12,
        time_range=range(1, 32),
    )

    for day in [1, 3, 5, 19, 20, 23, 24, 25, 29, 30, 31]:
        _override_transfer_data(
            datadir,
            s3_input_transfer_data_bucket_name,
            year=2019,
            data_month=12,
            data_day=day,
            input_folder="inputs/daily_hiding_slow_transfers",
        )

    expected_practice_metrics_output_key = "2019-12-practiceMetrics.json"

    expected_practice_metrics = _read_json(
        datadir / "expected_outputs" / "practiceMetricsHidingSlowTransfers.json"
    )

    expected_metadata = {
        "metrics-calculator-version": build_tag,
        "date-anchor": "2020-01-30T18:44:49+00:00",
        "number-of-months": "2",
    }

    s3_metrics_output_path = "v8/2019/12/"

    try:
        main()

        practice_metrics_s3_path = f"{s3_metrics_output_path}{expected_practice_metrics_output_key}"

        actual_practice_metrics = _read_s3_json(output_metrics_bucket, practice_metrics_s3_path)

        actual_practice_metrics_s3_metadata = _read_s3_metadata(
            output_metrics_bucket, practice_metrics_s3_path
        )

        assert actual_practice_metrics["practices"] == expected_practice_metrics["practices"]

        assert actual_practice_metrics["ccgs"] == expected_practice_metrics["ccgs"]
        assert actual_practice_metrics_s3_metadata == expected_metadata

    finally:
        output_metrics_bucket.objects.all().delete()
        output_metrics_bucket.delete()
        input_transfer_bucket.objects.all().delete()
        input_transfer_bucket.delete()
        fake_s3.stop()
        environ.clear()


@pytest.mark.filterwarnings("ignore:Conversion of")
def test_reads_daily_input_files_and_outputs_metrics_to_s3_including_slow_transfers(datadir):
    fake_s3_access_key = "testing"
    fake_s3_secret_key = "testing"
    fake_s3_region = "eu-west-2"
    s3_output_metrics_bucket_name = "output-metrics-bucket"
    s3_input_transfer_data_bucket_name = "input-transfer-data-bucket"
    s3_organisation_metadata_bucket_name = "organisation-metadata-bucket"
    build_tag = a_string(7)

    fake_s3 = _build_fake_s3(fake_s3_host, fake_s3_port)
    fake_s3.start()

    date_anchor = "2020-01-30T18:44:49Z"

    environ["AWS_ACCESS_KEY_ID"] = fake_s3_access_key
    environ["AWS_SECRET_ACCESS_KEY"] = fake_s3_secret_key
    environ["AWS_DEFAULT_REGION"] = fake_s3_region

    environ["INPUT_TRANSFER_DATA_BUCKET"] = s3_input_transfer_data_bucket_name
    environ["OUTPUT_METRICS_BUCKET"] = s3_output_metrics_bucket_name
    environ["ORGANISATION_METADATA_BUCKET"] = s3_organisation_metadata_bucket_name
    environ["NUMBER_OF_MONTHS"] = "2"
    environ["DATE_ANCHOR"] = date_anchor
    environ["S3_ENDPOINT_URL"] = fake_s3_url
    environ["BUILD_TAG"] = build_tag

    s3 = boto3.resource(
        "s3",
        endpoint_url=fake_s3_url,
        aws_access_key_id=fake_s3_access_key,
        aws_secret_access_key=fake_s3_secret_key,
        config=Config(signature_version="s3v4"),
        region_name=fake_s3_region,
    )

    output_metrics_bucket = _build_fake_s3_bucket(s3_output_metrics_bucket_name, s3)
    organisation_metadata_bucket = _build_fake_s3_bucket(s3_organisation_metadata_bucket_name, s3)

    organisation_metadata_file = str(datadir / "inputs" / "organisationMetadata.json")
    organisation_metadata_bucket.upload_file(
        organisation_metadata_file, "v2/2020/1/organisationMetadata.json"
    )

    input_transfer_bucket = _build_fake_s3_bucket(s3_input_transfer_data_bucket_name, s3)

    _upload_template_transfer_data(
        datadir,
        s3_input_transfer_data_bucket_name,
        year=2019,
        data_month=11,
        time_range=range(1, 31),
    )
    _override_transfer_data(
        datadir,
        s3_input_transfer_data_bucket_name,
        year=2019,
        data_month=11,
        data_day=1,
        input_folder="inputs/daily_including_slow_transfers",
    )

    _upload_template_transfer_data(
        datadir,
        s3_input_transfer_data_bucket_name,
        year=2019,
        data_month=12,
        time_range=range(1, 32),
    )

    for day in [1, 3, 5, 19, 20, 23, 24, 25, 30, 31]:
        _override_transfer_data(
            datadir,
            s3_input_transfer_data_bucket_name,
            year=2019,
            data_month=12,
            data_day=day,
            input_folder="inputs/daily_including_slow_transfers",
        )

    expected_practice_metrics_output_key = "2019-12-practiceMetrics.json"

    expected_practice_metrics_including_slow_transfers = _read_json(
        datadir / "expected_outputs" / "practiceMetricsIncludingSlowTransfers.json"
    )
    expected_national_metrics_output_key = "2019-12-nationalMetrics.json"
    expected_national_metrics = _read_json(
        datadir / "expected_outputs" / "nationalMetricsIncludingSlowTransfers.json"
    )

    expected_metadata = {
        "metrics-calculator-version": build_tag,
        "date-anchor": "2020-01-30T18:44:49+00:00",
        "number-of-months": "2",
    }

    s3_metrics_output_path = "v9/2019/12/"

    try:
        main()

        practice_metrics_s3_path = f"{s3_metrics_output_path}{expected_practice_metrics_output_key}"

        actual_practice_metrics_including_slow_transfers = _read_s3_json(
            output_metrics_bucket, practice_metrics_s3_path
        )

        national_metrics_s3_path = (
            f"{s3_metrics_output_path}" f"{expected_national_metrics_output_key}"
        )
        actual_national_metrics = _read_s3_json(output_metrics_bucket, national_metrics_s3_path)

        actual_practice_metrics_s3_metadata_including_slow_transfers = _read_s3_metadata(
            output_metrics_bucket, practice_metrics_s3_path
        )
        actual_national_metrics_s3_metadata = _read_s3_metadata(
            output_metrics_bucket, national_metrics_s3_path
        )

        assert (
            actual_practice_metrics_including_slow_transfers["practices"]
            == expected_practice_metrics_including_slow_transfers["practices"]
        )
        assert (
            actual_practice_metrics_including_slow_transfers["ccgs"]
            == expected_practice_metrics_including_slow_transfers["ccgs"]
        )
        assert actual_national_metrics["metrics"] == expected_national_metrics["metrics"]

        assert actual_practice_metrics_s3_metadata_including_slow_transfers == expected_metadata
        assert actual_national_metrics_s3_metadata == expected_metadata

    finally:
        output_metrics_bucket.objects.all().delete()
        output_metrics_bucket.delete()
        input_transfer_bucket.objects.all().delete()
        input_transfer_bucket.delete()
        fake_s3.stop()
        environ.clear()
