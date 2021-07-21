from datetime import timedelta
from unittest.mock import Mock
import pyarrow as pa

from prmcalculator.domain.gp2gp.transfer import Transfer, TransferOutcome, TransferStatus, Practice
from prmcalculator.pipeline.io import PlatformMetricsIO
from prmcalculator.utils.reporting_window import MonthlyReportingWindow
from tests.builders.common import a_datetime, a_string

_OVERFLOW_MONTH = 1
_OVERFLOW_YEAR = 2021

_METRIC_MONTH = 12
_METRIC_YEAR = 2020

_integrated_date_requested = a_datetime()
_integrated_sla_duration = timedelta(days=2, hours=19, minutes=0, seconds=41)
_integrated_date_completed = _integrated_date_requested + _integrated_sla_duration

_TRANSFER_LIST = [
    Transfer(
        conversation_id="123",
        sla_duration=_integrated_sla_duration,
        requesting_practice=Practice(asid="213125436412", supplier="Vision"),
        sending_practice=Practice(asid="123215421254", supplier="EMIS Web"),
        sender_error_code=None,
        final_error_codes=[],
        intermediate_error_codes=[],
        outcome=TransferOutcome(status=TransferStatus.INTEGRATED_ON_TIME, failure_reason=None),
        date_requested=_integrated_date_requested,
        date_completed=_integrated_date_completed,
    )
]


_TRANSFER_DATA_DICT = {
    "conversation_id": ["123"],
    "sla_duration": [241241],
    "requesting_practice_asid": ["213125436412"],
    "sending_practice_asid": ["123215421254"],
    "requesting_supplier": ["Vision"],
    "sending_supplier": ["EMIS Web"],
    "sender_error_code": [None],
    "final_error_codes": [[]],
    "intermediate_error_codes": [[]],
    "status": ["INTEGRATED_ON_TIME"],
    "failure_reason": [None],
    "date_requested": [_integrated_date_requested],
    "date_completed": [_integrated_date_completed],
}


def test_read_transfer_data():
    s3_manager = Mock()
    s3_manager.read_parquet.return_value = pa.Table.from_pydict(_TRANSFER_DATA_DICT)

    date_anchor = a_datetime(year=_OVERFLOW_YEAR, month=_OVERFLOW_MONTH)
    reporting_window = MonthlyReportingWindow.prior_to(date_anchor)

    transfer_data_bucket = "test_transfer_data_bucket"

    metrics_io = PlatformMetricsIO(
        reporting_window=reporting_window,
        s3_data_manager=s3_manager,
        organisation_metadata_bucket=a_string(),
        transfer_data_bucket=transfer_data_bucket,
        data_platform_metrics_bucket=a_string(),
    )

    expected_path = (
        f"s3://{transfer_data_bucket}/v3/{_METRIC_YEAR}/{_METRIC_MONTH}/transfers.parquet"
    )

    expected_data = _TRANSFER_LIST

    actual_data = metrics_io.read_transfer_data()

    assert actual_data == expected_data

    s3_manager.read_parquet.assert_called_once_with(expected_path)
