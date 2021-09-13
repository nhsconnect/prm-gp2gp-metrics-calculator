from datetime import timedelta
from unittest.mock import Mock, call
import pyarrow as pa

from prmcalculator.domain.gp2gp.transfer import (
    Transfer,
    TransferOutcome,
    TransferStatus,
    Practice,
    TransferFailureReason,
)
from prmcalculator.pipeline.io import PlatformMetricsIO
from prmcalculator.utils.reporting_window import MonthlyReportingWindow
from tests.builders.common import a_datetime, a_string

_DATE_ANCHOR_MONTH = 1
_DATE_ANCHOR_YEAR = 2021

_METRIC_MONTH = 12
_METRIC_YEAR = 2020

_integrated_date_requested = a_datetime()
_integrated_sla_duration = timedelta(days=2, hours=19, minutes=0, seconds=41)
_integrated_date_completed = _integrated_date_requested + _integrated_sla_duration

_integrated_late_date_requested = a_datetime()
_integrated_late_sla_duration = timedelta(days=9, hours=0, minutes=0, seconds=0)
_integrated_late_date_completed = _integrated_late_date_requested + _integrated_late_sla_duration

_INTEGRATED_TRANSFER = Transfer(
    conversation_id="123",
    sla_duration=_integrated_sla_duration,
    requesting_practice=Practice(asid="213125436412", supplier="SupplierA"),
    outcome=TransferOutcome(status=TransferStatus.INTEGRATED_ON_TIME, failure_reason=None),
    date_requested=_integrated_date_requested,
)


_INTEGRATED_LATE_TRANSFER = Transfer(
    conversation_id="456",
    sla_duration=_integrated_late_sla_duration,
    requesting_practice=Practice(asid="121212121212", supplier="SupplierB"),
    outcome=TransferOutcome(
        status=TransferStatus.PROCESS_FAILURE, failure_reason=TransferFailureReason.INTEGRATED_LATE
    ),
    date_requested=_integrated_late_date_requested,
)


_INTEGRATED_TRANSFER_DATA_DICT = {
    "conversation_id": ["123"],
    "sla_duration": [241241],
    "requesting_practice_asid": ["213125436412"],
    "requesting_supplier": ["SupplierA"],
    "status": ["INTEGRATED_ON_TIME"],
    "failure_reason": [None],
    "date_requested": [_integrated_date_requested],
}


_INTEGRATED_LATE_TRANSFER_DATA_DICT = {
    "conversation_id": ["456"],
    "sla_duration": [777600],
    "requesting_practice_asid": ["121212121212"],
    "requesting_supplier": ["SupplierB"],
    "status": ["PROCESS_FAILURE"],
    "failure_reason": ["Integrated Late"],
    "date_requested": [_integrated_late_date_requested],
}


def test_read_transfer_data():
    s3_manager = Mock()
    s3_manager.read_parquet.return_value = pa.Table.from_pydict(_INTEGRATED_TRANSFER_DATA_DICT)

    date_anchor = a_datetime(year=_DATE_ANCHOR_YEAR, month=_DATE_ANCHOR_MONTH)
    reporting_window = MonthlyReportingWindow.prior_to(date_anchor=date_anchor, number_of_months=1)

    transfer_data_bucket = "test_transfer_data_bucket"

    metrics_io = PlatformMetricsIO(
        reporting_window=reporting_window,
        s3_data_manager=s3_manager,
        organisation_metadata_bucket=a_string(),
        transfer_data_bucket=transfer_data_bucket,
        data_platform_metrics_bucket=a_string(),
        output_metadata={},
    )

    expected_path = (
        f"s3://{transfer_data_bucket}/v4/{_METRIC_YEAR}/{_METRIC_MONTH}/transfers.parquet"
    )

    expected_data = [_INTEGRATED_TRANSFER]

    actual_data = metrics_io.read_transfer_data()

    assert actual_data == expected_data

    s3_manager.read_parquet.assert_called_once_with(expected_path)


def test_read_transfer_data_from_multiple_files():
    s3_manager = Mock()
    s3_manager.read_parquet.side_effect = [
        pa.Table.from_pydict(_INTEGRATED_TRANSFER_DATA_DICT),
        pa.Table.from_pydict(_INTEGRATED_LATE_TRANSFER_DATA_DICT),
    ]

    date_anchor = a_datetime(year=_DATE_ANCHOR_YEAR, month=_DATE_ANCHOR_MONTH)
    reporting_window = MonthlyReportingWindow.prior_to(date_anchor=date_anchor, number_of_months=2)

    transfer_data_bucket = "test_transfer_data_bucket"

    metrics_io = PlatformMetricsIO(
        reporting_window=reporting_window,
        s3_data_manager=s3_manager,
        organisation_metadata_bucket=a_string(),
        transfer_data_bucket=transfer_data_bucket,
        data_platform_metrics_bucket=a_string(),
        output_metadata={},
    )

    expected_calls = [
        call(f"s3://{transfer_data_bucket}/v4/{_METRIC_YEAR}/{_METRIC_MONTH}/transfers.parquet"),
        call(
            f"s3://{transfer_data_bucket}/v4/{_METRIC_YEAR}/{_METRIC_MONTH - 1}/transfers.parquet"
        ),
    ]

    expected_data = [_INTEGRATED_TRANSFER, _INTEGRATED_LATE_TRANSFER]

    actual_data = metrics_io.read_transfer_data()

    assert actual_data == expected_data

    s3_manager.read_parquet.assert_has_calls(expected_calls)
