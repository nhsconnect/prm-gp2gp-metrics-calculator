from typing import List
from unittest.mock import Mock

from dateutil.tz import tzutc
from datetime import datetime
from freezegun import freeze_time

from prmcalculator.domain.practice.deprecated.metrics_presentation_deprecated import (
    construct_practice_metrics_presentation_deprecated,
    PracticeSummaryDeprecated,
)
from prmcalculator.domain.ods_portal.organisation_metadata import CcgDetails


@freeze_time(datetime(year=2019, month=6, day=2, hour=23, second=42), tz_offset=0)
def test_has_correct_generated_on_given_time():
    practice_summaries: List[PracticeSummaryDeprecated] = []
    ccgs: List[CcgDetails] = []

    expected_generated_on = datetime(year=2019, month=6, day=2, hour=23, second=42, tzinfo=tzutc())

    actual = construct_practice_metrics_presentation_deprecated(practice_summaries, ccgs)

    assert actual.generated_on == expected_generated_on


def test_has_correct_practice_summaries():
    practice_summaries: List[PracticeSummaryDeprecated] = [Mock(), Mock()]
    ccgs: List[CcgDetails] = []

    actual = construct_practice_metrics_presentation_deprecated(practice_summaries, ccgs)

    assert actual.practices == practice_summaries


def test_has_correct_ccgs():
    practice_summaries: List[PracticeSummaryDeprecated] = []
    ccgs: List[CcgDetails] = [Mock(), Mock()]

    actual = construct_practice_metrics_presentation_deprecated(practice_summaries, ccgs)

    assert actual.ccgs == ccgs
