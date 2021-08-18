from datetime import timedelta

from prmcalculator.domain.gp2gp.transfer import Practice
from prmcalculator.domain.ods_portal.organisation_metadata import PracticeDetails
from prmcalculator.domain.practice.construct_practice_transfer_metrics import (
    construct_practice_transfer_metrics,
)
from prmcalculator.domain.practice.practice_lookup import PracticeLookup
from prmcalculator.domain.practice.practice_transfer_metrics import PracticeTransferMetrics
from tests.builders.common import a_string
from tests.builders.gp2gp import build_transfer


def test_returns_dict_that_maps_ods_code_to_practice_transfer_metrics():
    ods_code = "A1234"
    lookup = PracticeLookup(
        [
            PracticeDetails(
                asids=["121212121212", "343434343434"], ods_code=ods_code, name=a_string()
            )
        ]
    )
    transfers = [
        build_transfer(
            requesting_practice=Practice(asid="343434343434", supplier=a_string(12)),
            sla_duration=timedelta(days=1),
        ),
        build_transfer(
            requesting_practice=Practice(asid="121212121212", supplier=a_string(12)),
            sla_duration=timedelta(days=2),
        ),
    ]

    practice_transfer_metrics = construct_practice_transfer_metrics(
        transfers=transfers, practice_lookup=lookup
    )

    assert type(practice_transfer_metrics[ods_code]) == PracticeTransferMetrics
