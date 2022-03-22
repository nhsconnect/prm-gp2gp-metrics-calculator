from unittest import mock
from unittest.mock import Mock

import pytest
from botocore.exceptions import ClientError

from prmcalculator.pipeline.io import PlatformMetricsIO, logger


def test_store_national_metrics_uri_ssm():
    ssm_manager = Mock()
    s3_uri = "some/uri/nationalMetrics.json"

    metrics_io = PlatformMetricsIO(
        s3_data_manager=Mock(),
        ssm_manager=ssm_manager,
        output_metadata={},
    )

    metrics_io.store_national_metrics_uri_ssm_param(
        s3_uri=s3_uri
    )

    ssm_manager.put_parameter.assert_called_once_with(
        Name="NATIONAL_METRICS_LOCATION",
        Value=s3_uri,
        Type="String"
    )


def test_exit_when_fails_to_store_national_metrics_uri_ssm():
    ssm_manager = Mock()
    s3_uri = "some/uri/nationalMetrics.json"

    client_error = ClientError({'Error': {'Code': '500', 'Message': 'Error Uploading'}}, "operation_name")
    ssm_manager.put_parameter.side_effect = client_error

    metrics_io = PlatformMetricsIO(
        s3_data_manager=Mock(),
        ssm_manager=ssm_manager,
        output_metadata={},
    )

    with pytest.raises(SystemExit):
        with mock.patch.object(logger, "error") as mock_log_error:
            metrics_io.store_national_metrics_uri_ssm_param(
                s3_uri=s3_uri
            )

    mock_log_error.assert_called_once_with(
        client_error
    )
