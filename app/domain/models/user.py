from dataclasses import dataclass
from typing import Optional
from enum import Enum

class NotifyChannel(str, Enum):
    EMAIL = "email"
    SMS = "sms"

@dataclass
class User:
    user_id: str
    name: str
    email: str
    phone: Optional[str]
    balance: float
    notify_channel: NotifyChannel
    version: int = 0      