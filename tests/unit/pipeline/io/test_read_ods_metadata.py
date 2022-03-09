from datetime import datetime
from unittest.mock import Mock

from dateutil.tz import UTC

from prmcalculator.domain.ods_portal.organisation_metadata import (
    CcgMetadata,
    OrganisationMetadata,
    PracticeMetadata,
)
from prmcalculator.pipeline.io import PlatformMetricsIO
from tests.builders.common import a_string

_DATE_ANCHOR_MONTH = 1
_DATE_ANCHOR_YEAR = 2021

_ORGANISATION_METADATA_OBJECT = OrganisationMetadata(
    generated_on=datetime(year=_DATE_ANCHOR_YEAR, month=_DATE_ANCHOR_MONTH, day=1, tzinfo=UTC),
    practices=[PracticeMetadata(ods_code="ABC", name="A Practice", asids=["123"])],
    ccgs=[CcgMetadata(ods_code="XYZ", name="A CCG", practices=["ABC"])],
)
_ORGANISATION_METADATA_DICT = {
    "generated_on": "2021-01-01T00:00:00.000000+00:00",
    "practices": [{"ods_code": "ABC", "name": "A Practice", "asids": ["123"]}],
    "ccgs": [{"ods_code": "XYZ", "name": "A CCG", "practices": ["ABC"]}],
}


def test_read_organisation_metadata():
    s3_manager = Mock()
    ods_bucket = a_string()
    s3_uri = (
        f"s3://{ods_bucket}/v2/{_DATE_ANCHOR_YEAR}/{_DATE_ANCHOR_MONTH}/organisationMetadata.json"
    )

    metrics_io = PlatformMetricsIO(
        s3_data_manager=s3_manager,
        output_metadata={},
    )

    s3_manager.read_json.return_value = _ORGANISATION_METADATA_DICT

    expected_data = _ORGANISATION_METADATA_OBJECT

    actual_data = metrics_io.read_ods_metadata(s3_uri=s3_uri)

    assert actual_data == expected_data

    s3_manager.read_json.assert_called_once_with(s3_uri)
