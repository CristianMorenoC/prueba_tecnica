from typing import Optional
from enum import Enum
from pydantic import BaseModel
from datetime import datetime


class Status(str, Enum):
    ACTIVE = "active"
    CANCELLED = "cancelled"


class Subscription(BaseModel):
    user_id: str
    fund_id: str
    amount: float
    status: Status
    created_at: Optional[str] = datetime.now().isoformat()
    cancelled_at: Optional[str] = None
