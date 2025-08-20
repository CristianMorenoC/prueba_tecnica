from dataclasses import dataclass
from enum import Enum


class UserStatus(str, Enum):
    ACTIVE = "active"
    INACTIVE = "inactive"


@dataclass
class Credentials:
    username: str
    hashed_password: str
    user_id: str
    status: UserStatus
    version: int = 0
