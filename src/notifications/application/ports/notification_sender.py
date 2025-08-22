from abc import ABC, abstractmethod
from typing import List
from domain.models.notification import NotificationMessage


class NotificationSenderPort(ABC):
    """Port for sending notifications"""
    
    @abstractmethod
    async def send_email(self, message: NotificationMessage) -> bool:
        """Send email notification"""
        pass
    
    @abstractmethod
    async def send_sms(self, message: NotificationMessage) -> bool:
        """Send SMS notification"""
        pass


class ContactManagerPort(ABC):
    """Port for managing contacts in SNS"""
    
    @abstractmethod
    async def subscribe_email(self, email: str) -> str:
        """Subscribe email to SNS topic and return subscription ARN"""
        pass
    
    @abstractmethod
    async def subscribe_phone(self, phone: str) -> str:
        """Subscribe phone to SNS topic and return subscription ARN"""
        pass
    
    @abstractmethod
    async def unsubscribe(self, subscription_arn: str) -> bool:
        """Unsubscribe from SNS topic"""
        pass