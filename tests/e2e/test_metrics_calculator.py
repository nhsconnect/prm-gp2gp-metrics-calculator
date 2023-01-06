import json

# import os
import sys
from datetime import datetime
from io import BytesIO
from os import environ
from threading import Thread
from unittest import mock
from unittest.mock import ANY

import boto3
import pyarrow as pa

# import pytest
from botocore.config import Config

# from moto import mock_ssm
from moto.server import DomainDispatcherApplication, create_backend_app
from pyarrow._s3fs import S3FileSystem
from pyarrow.parquet import write_table
from werkzeug.serving import make_server

from prmcalculator.pipeline.main import logger, main
from prmcalculator.utils.add_leading_zero import add_leading_zero
from tests.builders.common import a_string, an_integer


class ThreadedServer:
    def __init__(self, server):
        self._server = server
        self._thread = Thread(target=server.serve_forever)

    def start(self):
        self._thread.start()

    def stop(self):
        self._server.shutdown()
        self._thread.join()


FAKE_AWS_HOST = "127.0.0.1"
FAKE_AWS_PORT = an_integer(8000, 8080)
FAKE_AWS_URL = f"http://{FAKE_AWS_HOST}:{FAKE_AWS_PORT}"
FAKE_S3_ACCESS_KEY = "testing"
FAKE_S3_SECRET_KEY = "testing"
FAKE_S3_REGION = "eu-west-2"

S3_OUTPUT_METRICS_BUCKET_NAME = "output-metrics-bucket"
S3_INPUT_TRANSFER_DATA_BUCKET_NAME = "input-transfer-data-bucket"

NATIONAL_METRICS_S3_PATH_PARAM_NAME = "registrations/national-metrics/test-param-name"
PRACTICE_METRICS_S3_PATH_PARAM_NAME = "registrations/practice-metrics/test-param-name"

BUILD_TAG = a_string(7)


def _setup():
    s3_client = boto3.resource(
        "s3",
        endpoint_url=FAKE_AWS_URL,
        aws_access_key_id=FAKE_S3_ACCESS_KEY,
        aws_secret_access_key=FAKE_S3_SECRET_KEY,
        config=Config(signature_version="s3v4"),
        region_name=FAKE_S3_REGION,
    )

    environ["AWS_ACCESS_KEY_ID"] = FAKE_S3_ACCESS_KEY
    environ["AWS_SECRET_ACCESS_KEY"] = FAKE_S3_SECRET_KEY
    environ["AWS_DEFAULT_REGION"] = FAKE_S3_REGION

    environ["INPUT_TRANSFER_DATA_BUCKET"] = S3_INPUT_TRANSFER_DATA_BUCKET_NAME
    environ["OUTPUT_METRICS_BUCKET"] = S3_OUTPUT_METRICS_BUCKET_NAME

    environ["NATIONAL_METRICS_S3_PATH_PARAM_NAME"] = NATIONAL_METRICS_S3_PATH_PARAM_NAME
    environ["PRACTICE_METRICS_S3_PATH_PARAM_NAME"] = PRACTICE_METRICS_S3_PATH_PARAM_NAME

    environ["S3_ENDPOINT_URL"] = FAKE_AWS_URL
    environ["BUILD_TAG"] = BUILD_TAG

    fake_s3 = _build_fake_s3(FAKE_AWS_HOST, FAKE_AWS_PORT)
    return fake_s3, s3_client


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


def _build_fake_s3(host, port):
    app = DomainDispatcherApplication(create_backend_app, "s3")
    server = make_server(host, port, app)
    return ThreadedServer(server)


def _build_fake_s3_bucket(bucket_name: str, s3):
    s3_fake_bucket = s3.Bucket(bucket_name)
    s3_fake_bucket.create()
    return s3_fake_bucket


def _read_s3_metadata(bucket, key):
    return bucket.Object(key).get()["Metadata"]


def _delete_bucket_with_objects(s3_bucket):
    s3_bucket.objects.all().delete()
    s3_bucket.delete()


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
            ("requesting_practice_name", pa.string()),
            ("requesting_practice_ods_code", pa.string()),
            ("requesting_practice_sicbl_name", pa.string()),
            ("requesting_practice_sicbl_ods_code", pa.string()),
        ]
    )

    transfers_dictionary = _read_parquet_columns_json(input_transfer_parquet_columns_json)
    transfers_table = pa.table(data=transfers_dictionary, schema=transfer_parquet_schema)

    write_table(
        table=transfers_table,
        where=s3_path,
        filesystem=S3FileSystem(endpoint_override=FAKE_AWS_URL),
    )


def _get_s3_path(bucket_name, year, month, day):
    return (
        f"{bucket_name}/v11/cutoff-14/{year}/{month}/{day}/{year}-{month}-{day}-transfers.parquet"
    )


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


def _get_ssm_param(ssm_parameter_name):
    session = boto3.Session()
    ssm_client = session.client("ssm")
    param = ssm_client.get_parameter(Name=ssm_parameter_name, WithDecryption=True)
    return param["Parameter"]["Value"]


def test_exception_in_main():
    with mock.patch.object(sys, "exit") as exitSpy:
        with mock.patch.object(logger, "error") as mock_log_error:
            main()

    mock_log_error.assert_called_with(
        ANY,
        extra={"event": "FAILED_TO_RUN_MAIN", "config": "{}"},
    )

    exitSpy.assert_called_with("Failed to run main, exiting...")
