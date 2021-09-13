from prmcalculator.pipeline.io import PlatformMetricsS3UriResolver
from tests.builders.common import a_string, a_datetime


def test_resolver_returns_correct_ods_metadata_uri():
    ods_bucket_name = a_string()
    date_anchor = a_datetime()
    year = date_anchor.year
    month = date_anchor.month

    uri_resolver = PlatformMetricsS3UriResolver(ods_bucket=ods_bucket_name)

    actual = uri_resolver.ods_metadata(year, month)

    expected = f"s3://{ods_bucket_name}/v2/{year}/{month}/organisationMetadata.json"

    assert actual == expected
