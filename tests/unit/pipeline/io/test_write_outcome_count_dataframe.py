from unittest.mock import Mock
import polars as pl

from prmcalculator.pipeline.io import PlatformMetricsIO
from tests.builders.common import a_string

_DATE_ANCHOR_MONTH = 1
_DATE_ANCHOR_YEAR = 2021


def test_given_dataframe_will_write_csv():
    s3_manager = Mock()
    data_platform_metrics_bucket = a_string()
    s3_key = f"v6/{_DATE_ANCHOR_YEAR}/{_DATE_ANCHOR_MONTH}/supplier_pathway_outcome_counts.csv"
    s3_uri = f"s3://{data_platform_metrics_bucket}/{s3_key}"

    output_metadata = {"metadata-field": "metadata_value"}

    metrics_io = PlatformMetricsIO(
        s3_data_manager=s3_manager,
        output_metadata=output_metadata,
    )
    data = {"Fruit": ["Banana"]}
    df = pl.DataFrame(data)

    metrics_io.write_outcome_count(dataframe=df, s3_uri=s3_uri)

    expected_dataframe = df

    s3_manager.write_csv.assert_called_once_with(
        object_uri=s3_uri, dataframe=expected_dataframe, metadata=output_metadata
    )
