from typing import List

from prmcalculator.domain.gp2gp.transfer import Transfer, TransferStatus
from prmcalculator.domain.national.transfer_outcome_counter import TransferOutcomeCounter


class TransferOutcomes:
    def __init__(self):
        self.integrated_on_time = TransferOutcomeCounter()
        self.process_failure = TransferOutcomeCounter()
        self.technical_failure = TransferOutcomeCounter()
        self.unclassified_failure = TransferOutcomeCounter()

    @classmethod
    def group_transfers(cls, transfers: List[Transfer]):
        transfer_outcomes = cls()

        transfer_outcomes_counter_mapping = {
            TransferStatus.INTEGRATED_ON_TIME: transfer_outcomes.integrated_on_time,
            TransferStatus.PROCESS_FAILURE: transfer_outcomes.process_failure,
            TransferStatus.TECHNICAL_FAILURE: transfer_outcomes.technical_failure,
            TransferStatus.UNCLASSIFIED_FAILURE: transfer_outcomes.unclassified_failure,
        }

        for transfer in transfers:
            transfer_outcomes_counter_mapping[transfer.outcome.status].add_transfer(transfer)

        return transfer_outcomes
