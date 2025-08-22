from typing import Optional
from enum import Enum
from pydantic import BaseModel


class NotifyChannel(str, Enum):
    EMAIL = "email"
    SMS = "sms"


class User(BaseModel):
    user_id: str
    name: str
    email: str
    phone: Optional[str]
    balance: int
    notify_channel: NotifyChannel
