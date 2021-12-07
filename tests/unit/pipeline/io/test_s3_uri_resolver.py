from prmcalculator.pipeline.io import PlatformMetricsS3UriResolver
from tests.builders.common import a_datetime, a_string


def test_resolver_returns_correct_ods_metadata_uri():
    ods_bucket_name = a_string()
    date_anchor = a_datetime()
    year = date_anchor.year
    month = date_anchor.month

    uri_resolver = PlatformMetricsS3UriResolver(
        ods_bucket=ods_bucket_name,
        data_platform_metrics_bucket=a_string(),
        transfer_data_bucket=a_string(),
    )

    actual = uri_resolver.ods_metadata((year, month))

    expected = f"s3://{ods_bucket_name}/v2/{year}/{month}/organisationMetadata.json"

    assert actual == expected


def test_resolver_returns_correct_practice_metrics_uri_with_default_version():
    data_platform_metrics_bucket = a_string()
    date_anchor = a_datetime()
    year = date_anchor.year
    month = date_anchor.month

    uri_resolver = PlatformMetricsS3UriResolver(
        ods_bucket=a_string(),
        data_platform_metrics_bucket=data_platform_metrics_bucket,
        transfer_data_bucket=a_string(),
    )

    actual = uri_resolver.practice_metrics((year, month))

    expected = (
        f"s3://{data_platform_metrics_bucket}/v7/{year}/{month}/{year}-{month}-practiceMetrics.json"
    )

    assert actual == expected


def test_resolver_returns_correct_practice_metrics_uri_with_specified_version():
    data_platform_metrics_bucket = a_string()
    date_anchor = a_datetime()
    year = date_anchor.year
    month = date_anchor.month

    uri_resolver = PlatformMetricsS3UriResolver(
        ods_bucket=a_string(),
        data_platform_metrics_bucket=data_platform_metrics_bucket,
        transfer_data_bucket=a_string(),
    )

    actual = uri_resolver.practice_metrics((year, month), "v2")

    expected = (
        f"s3://{data_platform_metrics_bucket}/v2/{year}/{month}/{year}-{month}-practiceMetrics.json"
    )

    assert actual == expected


def test_resolver_returns_correct_national_metrics_uri():
    data_platform_metrics_bucket = a_string()
    date_anchor = a_datetime()
    year = date_anchor.year
    month = date_anchor.month

    uri_resolver = PlatformMetricsS3UriResolver(
        ods_bucket=a_string(),
        data_platform_metrics_bucket=data_platform_metrics_bucket,
        transfer_data_bucket=a_string(),
    )

    actual = uri_resolver.national_metrics((year, month))

    expected = (
        f"s3://{data_platform_metrics_bucket}/v7/{year}/{month}/{year}-{month}-nationalMetrics.json"
    )

    assert actual == expected


def test_resolver_returns_correct_supplier_pathway_outcome_counts_uri():
    data_platform_metrics_bucket = a_string()
    date_anchor = a_datetime()
    year = date_anchor.year
    month = date_anchor.month

    uri_resolver = PlatformMetricsS3UriResolver(
        ods_bucket=a_string(),
        data_platform_metrics_bucket=data_platform_metrics_bucket,
        transfer_data_bucket=a_string(),
    )

    actual = uri_resolver.supplier_pathway_outcome_counts((year, month))

    s3_key = f"v7/{year}/{month}/{year}-{month}-supplier_pathway_outcome_counts.csv"
    expected = f"s3://{data_platform_metrics_bucket}/{s3_key}"

    assert actual == expected


def test_resolver_returns_correct_transfer_data_uris():
    transfer_data_bucket = a_string()

    metric_months = [(2021, 11), (2021, 12), (2022, 1)]

    uri_resolver = PlatformMetricsS3UriResolver(
        ods_bucket=a_string(),
        data_platform_metrics_bucket=a_string(),
        transfer_data_bucket=transfer_data_bucket,
    )

    actual = uri_resolver.transfer_data(metric_months)

    expected = [
        f"s3://{transfer_data_bucket}/v6/2021/11/2021-11-transfers.parquet",
        f"s3://{transfer_data_bucket}/v6/2021/12/2021-12-transfers.parquet",
        f"s3://{transfer_data_bucket}/v6/2022/1/2022-1-transfers.parquet",
    ]

    assert actual == expected
