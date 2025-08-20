from dataclasses import dataclass


@dataclass
class Fund:
    fund_id: str
    name: str
    min_amount: float
    category: str
    version: int = 0
