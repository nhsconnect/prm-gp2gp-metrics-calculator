import boto3
from moto import mock_s3
import polars as pl

from prmcalculator.utils.io.s3 import S3DataManager
from tests.unit.utils.io.s3 import MOTO_MOCK_REGION

SOME_METADATA = {"metadata_field": "metadata_value"}


@mock_s3
def test_writes_csv():
    conn = boto3.resource("s3", region_name=MOTO_MOCK_REGION)
    bucket = conn.create_bucket(Bucket="test_bucket")
    s3_manager = S3DataManager(conn)
    data = {"Fruit": ["Banana", "Strawberry"], "Colour": ["yellow", "red"], "Quantity": [2, 3]}
    df = pl.DataFrame(data)

    expected = b'"Fruit","Colour","Quantity"\n"Banana","yellow",2\n"Strawberry","red",3\n'

    s3_manager.write_csv(
        object_uri="s3://test_bucket/test_object.csv", dataframe=df, metadata=SOME_METADATA
    )

    actual = bucket.Object("test_object.csv").get()["Body"].read()

    assert actual == expected


@mock_s3
def test_writes_correct_content_type():
    conn = boto3.resource("s3", region_name=MOTO_MOCK_REGION)
    bucket = conn.create_bucket(Bucket="test_bucket")
    s3_manager = S3DataManager(conn)
    data = {"Fruit": ["Banana"]}
    df = pl.DataFrame(data)

    expected = "text/csv"

    s3_manager.write_csv(
        object_uri="s3://test_bucket/test_object.csv", dataframe=df, metadata=SOME_METADATA
    )

    actual = bucket.Object("test_object.csv").get()["ContentType"]

    assert actual == expected


@mock_s3
def test_writes_metadata_when_supplied():
    conn = boto3.resource("s3", region_name=MOTO_MOCK_REGION)
    bucket = conn.create_bucket(Bucket="test_bucket")
    s3_manager = S3DataManager(conn)
    data = {"Fruit": ["Banana"]}
    df = pl.DataFrame(data)

    metadata = {
        "metadata_field": "metadata_field_value",
        "second_metadata_field": "metadata_field_second_value",
    }

    s3_manager.write_csv(
        object_uri="s3://test_bucket/test_object.csv", dataframe=df, metadata=metadata
    )

    expected = metadata
    actual = bucket.Object("test_object.csv").get()["Metadata"]

    assert actual == expected
