from dataclasses import dataclass
from typing import Optional
from enum import Enum

class TransactionType(str, Enum):
    OPEN = "open"
    CANCEL = "cancel"

@dataclass
class Transaction:
    tx_id: str
    user_id: str
    fund_id: str
    amount: float
    transaction_type: TransactionType
    timestamp: str
    prev_balance: float
    new_balance: float
    version: int = 0  # For optimistic locking