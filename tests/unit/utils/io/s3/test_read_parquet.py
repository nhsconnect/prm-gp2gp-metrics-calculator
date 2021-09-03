from unittest import mock

import boto3
from moto import mock_s3
import pyarrow as pa
from pyarrow.parquet import write_table

from prmcalculator.utils.io.s3 import S3DataManager, logger
from tests.unit.utils.io.s3 import MOTO_MOCK_REGION


@mock_s3
def test_read_parquet_returns_dictionary():
    conn = boto3.resource("s3", region_name=MOTO_MOCK_REGION)
    bucket_name = "test_bucket"
    bucket = conn.create_bucket(Bucket=bucket_name)
    s3_object = bucket.Object("fruits.parquet")

    data = {"fruit": ["mango", "lemon"]}
    fruit_table = pa.table(data)
    writer = pa.BufferOutputStream()
    write_table(fruit_table, writer)
    body = bytes(writer.getvalue())
    s3_object.put(Body=body)

    s3_manager = S3DataManager(conn)
    actual_data = s3_manager.read_parquet(f"s3://{bucket_name}/fruits.parquet")

    expected_data = fruit_table

    assert actual_data == expected_data


@mock_s3
def test_will_log_reading_file_event():
    conn = boto3.resource("s3", region_name=MOTO_MOCK_REGION)
    bucket_name = "test_bucket"
    bucket = conn.create_bucket(Bucket=bucket_name)
    s3_object = bucket.Object("fruits.parquet")

    data = {"fruit": ["mango", "lemon"]}
    fruit_table = pa.table(data)
    writer = pa.BufferOutputStream()
    write_table(fruit_table, writer)
    body = bytes(writer.getvalue())
    s3_object.put(Body=body)

    s3_manager = S3DataManager(conn)
    s3_file_path = f"s3://{bucket_name}/fruits.parquet"

    with mock.patch.object(logger, "info") as mock_log_info:
        s3_manager.read_parquet(s3_file_path)
        mock_log_info.assert_called_once_with(
            f"Reading file from: {s3_file_path}", extra={"event": "READING_FILE_FROM_S3"}
        )
