from dataclasses import dataclass
from typing import Dict, List

from prmcalculator.domain.gp2gp.transfer import Transfer

ODSCode = str
PracticeTransfersDictByOds = Dict[ODSCode, List[Transfer]]


@dataclass(frozen=True)
class CCG:
    ccg_ods_code: ODSCode
    ccg_name: str
    practices_ods_codes: List[str]


CCGTransfersDictByOds = Dict[ODSCode, CCG]


@dataclass(frozen=True)
class Practice:
    ods_code: ODSCode
    name: str
    transfers: List[Transfer]
    ccg_ods_code: ODSCode
    ccg_name: str


class PracticeTransfers:
    ods_code: List[Transfer]


class TransfersService:
    def __init__(self, transfers: List[Transfer], observability_probe):
        self._transfers = transfers
        self._observability_probe = observability_probe
        self._grouped_transfers_by_practice = self.group_transfers_by_practice()
        self._grouped_practices_by_ccg = self.group_practices_by_ccg()

    def group_transfers_by_practice(self) -> List[Practice]:
        practice_list = []
        for practice_transfers in self._group_practice_transfers_by_ods_code().values():
            latest_transfer = self._get_latest_transfer(practice_transfers)

            if latest_transfer.requesting_practice.ccg_ods_code is None:
                self._observability_probe.record_unknown_practice_ccg_ods_code_for_transfer(
                    latest_transfer
                )
                continue

            practice_list.append(
                Practice(
                    ods_code=latest_transfer.requesting_practice.ods_code,
                    name=latest_transfer.requesting_practice.name,
                    ccg_ods_code=latest_transfer.requesting_practice.ccg_ods_code,
                    ccg_name=latest_transfer.requesting_practice.ccg_name,
                    transfers=practice_transfers,
                )
            )
        return practice_list

    def _group_practice_transfers_by_ods_code(self) -> PracticeTransfersDictByOds:
        practice_transfers_by_ods_code: PracticeTransfersDictByOds = {}
        for transfer in self._transfers:
            if transfer.requesting_practice.ods_code is None:
                self._observability_probe.record_unknown_practice_ods_code_for_transfer(transfer)
                continue

            self._add_transfer_to_ods_dictionary(practice_transfers_by_ods_code, transfer)
        return practice_transfers_by_ods_code

    @staticmethod
    def _get_latest_transfer(practice_transfers):
        latest_transfer = practice_transfers[0]
        for transfer in practice_transfers:
            if transfer.date_requested > latest_transfer.date_requested:
                latest_transfer = transfer
        return latest_transfer

    @staticmethod
    def _add_transfer_to_ods_dictionary(practice_transfers, transfer):
        if transfer.requesting_practice.ods_code not in practice_transfers:
            practice_transfers[transfer.requesting_practice.ods_code] = []
        practice_transfers[transfer.requesting_practice.ods_code].append(transfer)

    def group_practices_by_ccg(self) -> List[CCG]:
        ccgs_dict: CCGTransfersDictByOds = {}
        for practice in self._grouped_transfers_by_practice:
            self._add_practice_to_ccg_ods_dictionary(ccgs_dict, practice)

        return list(ccgs_dict.values())

    @staticmethod
    def _add_practice_to_ccg_ods_dictionary(ccgs_dict, practice):
        if practice.ccg_ods_code not in ccgs_dict:
            ccgs_dict[practice.ccg_ods_code] = CCG(
                ccg_name=practice.ccg_name,
                ccg_ods_code=practice.ccg_ods_code,
                practices_ods_codes=[],
            )
        ccgs_dict[practice.ccg_ods_code].practices_ods_codes.append(practice.ods_code)

    @property
    def grouped_practices_by_ods(self) -> List[Practice]:
        return self._grouped_transfers_by_practice

    @property
    def grouped_practices_by_ccg(self) -> List[CCG]:
        return self._grouped_practices_by_ccg
