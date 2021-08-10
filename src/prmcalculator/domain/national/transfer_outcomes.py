from typing import List

from prmcalculator.domain.gp2gp.transfer import Transfer, TransferStatus
from prmcalculator.domain.national.transfer_outcome_counter import TransferOutcomeCounter


class TransferOutcomes:
    def __init__(self):
        self.integrated_on_time = TransferOutcomeCounter()
        self.process_failure = TransferOutcomeCounter()
        self.technical_failure = TransferOutcomeCounter()
        self.unclassified_failure = TransferOutcomeCounter()

    # flake8: noqa: C901
    @classmethod
    def group_transfers(cls, transfers: List[Transfer]):
        transfer_outcomes = cls()

        for transfer in transfers:
            if transfer.outcome.status == TransferStatus.INTEGRATED_ON_TIME:
                transfer_outcomes.integrated_on_time.add_transfer(transfer)
            elif transfer.outcome.status == TransferStatus.PROCESS_FAILURE:
                transfer_outcomes.process_failure.add_transfer(transfer)
            elif transfer.outcome.status == TransferStatus.TECHNICAL_FAILURE:
                transfer_outcomes.technical_failure.add_transfer(transfer)
            elif transfer.outcome.status == TransferStatus.UNCLASSIFIED_FAILURE:
                transfer_outcomes.unclassified_failure.add_transfer(transfer)

        return transfer_outcomes
