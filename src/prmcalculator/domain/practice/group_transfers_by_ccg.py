from dataclasses import dataclass
from typing import Dict, List

from prmcalculator.domain.practice.group_transfers_by_practice import Practice

ODSCode = str


@dataclass(frozen=True)
class CCG:
    ccg_ods_code: ODSCode
    ccg_name: str
    practices_ods_codes: List[str]


def group_transfers_by_ccg(practices: List[Practice], observability_probe) -> List[CCG]:
    ccgs_dict: CCGTransfersDictByOds = {}
    for practice in practices:
        if practice.ccg_ods_code not in ccgs_dict:
            ccgs_dict[practice.ccg_ods_code] = CCG(
                ccg_name=practice.ccg_name,
                ccg_ods_code=practice.ccg_ods_code,
                practices_ods_codes=[],
            )
        ccgs_dict[practice.ccg_ods_code].practices_ods_codes.append(practice.ods_code)

    return list(ccgs_dict.values())


CCGTransfersDictByOds = Dict[ODSCode, CCG]
