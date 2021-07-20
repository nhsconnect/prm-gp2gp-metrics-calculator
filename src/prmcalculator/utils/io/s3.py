import json
from datetime import datetime
from io import BytesIO
from urllib.parse import urlparse
import pyarrow.parquet as pq


def _serialize_datetime(obj):
    if isinstance(obj, datetime):
        return obj.isoformat()
    raise TypeError(f"Type {type(obj)} is not JSON serializable")


class S3DataManager:
    def __init__(self, client):
        self._client = client

    def _object_from_uri(self, uri):
        object_url = urlparse(uri)
        s3_bucket = object_url.netloc
        s3_key = object_url.path.lstrip("/")
        return self._client.Object(s3_bucket, s3_key)

    def read_json(self, object_uri):
        s3_object = self._object_from_uri(object_uri)
        response = s3_object.get()
        body = response["Body"].read()
        return json.loads(body.decode("utf8"))

    def write_json(self, object_uri, data):
        s3_object = self._object_from_uri(object_uri)
        body = json.dumps(data, default=_serialize_datetime).encode("utf8")
        s3_object.put(Body=body, ContentType="application/json")

    def read_parquet(self, object_uri: str) -> dict:
        s3_object = self._object_from_uri(object_uri)
        response = s3_object.get()
        body = BytesIO(response["Body"].read())
        return pq.read_table(body).to_pydict()
