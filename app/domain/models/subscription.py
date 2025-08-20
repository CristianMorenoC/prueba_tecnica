from dataclasses import dataclass
from typing import Optional
from datetime import datetime
from enum import Enum

class Status(str, Enum):
    ACTIVE = "active"
    CANCELLED = "cancelled"

@dataclass
class Subscription:
    user_id: str
    fund_id: str
    amount: float
    status: Status
    created_at: str
    cancelled_at: Optional[str] = None
    version: int = 0  # For optimistic locking
