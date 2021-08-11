from prmcalculator.domain.national.transfer_outcomes import TransferOutcomes
from tests.builders.gp2gp import (
    a_transfer_integrated_between_3_and_8_days,
    a_transfer_with_a_final_error,
    a_transfer_that_was_never_integrated,
    a_transfer_integrated_beyond_8_days,
    a_transfer_where_a_copc_triggered_an_error,
    a_transfer_where_no_core_ehr_was_sent,
    a_transfer_where_the_request_was_never_acknowledged,
)


def test_returns_grouped_transfer_outcomes():
    transfers = [
        a_transfer_integrated_between_3_and_8_days(),
        a_transfer_with_a_final_error(),
        a_transfer_where_the_request_was_never_acknowledged(),
        a_transfer_where_no_core_ehr_was_sent(),
        a_transfer_that_was_never_integrated(),
        a_transfer_integrated_beyond_8_days(),
        a_transfer_where_a_copc_triggered_an_error(),
    ]

    transfer_outcome_groups = TransferOutcomes.group_transfers(transfers)

    assert transfer_outcome_groups.integrated_on_time.total == 1
    assert transfer_outcome_groups.technical_failure.total == 3
    assert transfer_outcome_groups.process_failure.total == 2
    assert transfer_outcome_groups.unclassified_failure.total == 1
