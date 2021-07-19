from datetime import datetime
import json
import logging
from io import BytesIO
from os import environ
from threading import Thread
import boto3
from botocore.config import Config
from moto.server import DomainDispatcherApplication, create_backend_app
from pyarrow._s3fs import S3FileSystem
from pyarrow.parquet import write_table
import pyarrow as pa
from werkzeug.serving import make_server

from prmcalculator.pipeline.main import main

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
    return {
        column_name: _parse_dates(values) if column_name.startswith("date_") else values
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


def test_end_to_end_with_fake_s3(datadir):
    fake_s3_host = "127.0.0.1"
    fake_s3_port = 8887
    fake_s3_url = f"http://{fake_s3_host}:{fake_s3_port}"
    fake_s3_access_key = "testing"
    fake_s3_secret_key = "testing"
    fake_s3_region = "eu-west-2"
    s3_output_metrics_bucket_name = "output-metrics-bucket"
    s3_input_transfer_data_bucket_name = "input-transfer-data-bucket"
    s3_organisation_metadata_bucket_name = "organisation-metadata-bucket"
    fake_s3 = _build_fake_s3(fake_s3_host, fake_s3_port)
    fake_s3.start()
    environ["AWS_ACCESS_KEY_ID"] = fake_s3_access_key
    environ["AWS_SECRET_ACCESS_KEY"] = fake_s3_secret_key
    environ["AWS_DEFAULT_REGION"] = fake_s3_region
    environ["INPUT_TRANSFER_DATA_BUCKET"] = s3_input_transfer_data_bucket_name
    environ["OUTPUT_METRICS_BUCKET"] = s3_output_metrics_bucket_name
    environ["ORGANISATION_METADATA_BUCKET"] = s3_organisation_metadata_bucket_name
    environ["DATE_ANCHOR"] = "2020-01-30T18:44:49Z"
    environ["S3_ENDPOINT_URL"] = fake_s3_url

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

    _build_fake_s3_bucket(s3_input_transfer_data_bucket_name, s3)

    transfers_dictionary = _read_parquet_columns_json(
        datadir / "inputs" / "transfersParquetColumns.json"
    )

    transfers_table = pa.table(transfers_dictionary)

    write_table(
        table=transfers_table,
        where=f"{s3_input_transfer_data_bucket_name}/v3/2019/12/transfers.parquet",
        filesystem=S3FileSystem(endpoint_override=fake_s3_url),
    )

    expected_practice_metrics_output_key = "practiceMetrics.json"
    expected_practice_metrics = _read_json(datadir / "expected_outputs" / "practiceMetrics.json")

    s3_output_path = "v3/2019/12/"

    try:
        main()
        actual_practice_metrics = _read_s3_json(
            output_metrics_bucket, f"{s3_output_path}{expected_practice_metrics_output_key}"
        )

        assert actual_practice_metrics["practices"] == expected_practice_metrics["practices"]
        assert actual_practice_metrics["ccgs"] == expected_practice_metrics["ccgs"]
    finally:
        output_metrics_bucket.objects.all().delete()
        output_metrics_bucket.delete()
        fake_s3.stop()
