from enum import Enum
from pydantic import BaseModel


class TransactionType(str, Enum):
    OPEN = "open"
    CANCEL = "cancel"


class Transaction(BaseModel):
    user_id: str
    fund_id: str
    amount: float
    transaction_type: TransactionType
    timestamp: str
    prev_balance: float
    new_balance: float
