from dataclasses import dataclass
from typing import List


@dataclass
class PracticeDetails:
    ods_code: str
    name: str
    asids: List[str]
