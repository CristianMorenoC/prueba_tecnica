from typing import Dict, Any
from enum import Enum
from pydantic import BaseModel


class NotificationType(str, Enum):
    SUBSCRIPTION_CREATED = "subscription_created"
    SUBSCRIPTION_CANCELLED = "subscription_cancelled"
    USER_PROFILE_CREATED = "user_profile_created"


class NotificationChannel(str, Enum):
    EMAIL = "email"
    SMS = "sms"


class NotificationMessage(BaseModel):
    """Base notification message"""
    type: NotificationType
    channel: NotificationChannel
    recipient: str
    subject: str
    message: str
    metadata: Dict[str, Any] = {}


class SubscriptionNotification(NotificationMessage):
    """Notification for subscription events"""
    user_id: str
    fund_id: str
    
    def __init__(self, **data):
        super().__init__(**data)
        self.type = NotificationType.SUBSCRIPTION_CREATED if "created" in data.get("subject", "").lower() else NotificationType.SUBSCRIPTION_CANCELLED


class UserProfileNotification(NotificationMessage):
    """Notification for user profile creation"""
    user_id: str
    
    def __init__(self, **data):
        super().__init__(**data)
        self.type = NotificationType.USER_PROFILE_CREATED