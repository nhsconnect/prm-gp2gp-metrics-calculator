from datetime import datetime

from dateutil.tz import tzutc
from freezegun import freeze_time

from prmcalculator.domain.national.metrics_calculator import NationalMetricsMonth
from prmcalculator.domain.national.metrics_presentation import (
    construct_national_metrics_presentation,
)

from tests.builders.common import a_datetime

a_year = a_datetime().year
a_month = a_datetime().month


@freeze_time(datetime(year=2019, month=6, day=2, hour=23, second=42), tz_offset=0)
def test_has_correct_generated_on_given_time():
    national_metrics_month = NationalMetricsMonth(transfers=[], year=a_year, month=a_month)

    actual = construct_national_metrics_presentation([national_metrics_month])
    expected_generated_on = datetime(year=2019, month=6, day=2, hour=23, second=42, tzinfo=tzutc())

    assert actual.generated_on == expected_generated_on


def test_has_correct_metric_month_and_year():
    national_metrics_month = NationalMetricsMonth(transfers=[], year=a_year, month=a_month)

    actual = construct_national_metrics_presentation([national_metrics_month])

    assert len(actual.metrics) == 1
    assert actual.metrics[0].year == a_year
    assert actual.metrics[0].month == a_month
