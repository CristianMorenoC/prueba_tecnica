from typing import Dict, Any, Optional, Union
from enum import Enum
from pydantic import BaseModel, Field


class EventName(str, Enum):
    INSERT = "INSERT"
    MODIFY = "MODIFY"
    REMOVE = "REMOVE"


class DynamoDBImage(BaseModel):
    """DynamoDB attribute value representation"""
    PK: Optional[Dict[str, str]] = None
    SK: Optional[Dict[str, str]] = None
    user_id: Optional[Dict[str, str]] = None
    name: Optional[Dict[str, str]] = None
    email: Optional[Dict[str, str]] = None
    phone: Optional[Dict[str, str]] = None
    balance: Optional[Dict[str, Union[str, int]]] = None
    notify_channel: Optional[Dict[str, str]] = None
    fund_id: Optional[Dict[str, str]] = None
    amount: Optional[Dict[str, Union[str, int]]] = None
    status: Optional[Dict[str, str]] = None
    created_at: Optional[Dict[str, str]] = None
    cancelled_at: Optional[Dict[str, str]] = None


class DynamoDBStreamRecord(BaseModel):
    """DynamoDB Stream record structure"""
    eventID: str
    eventName: EventName
    eventVersion: str
    eventSource: str
    awsRegion: str
    dynamodb: Dict[str, Any]
    
    @property
    def new_image(self) -> Optional[DynamoDBImage]:
        """Get the new image from DynamoDB record"""
        if "NewImage" in self.dynamodb:
            return DynamoDBImage(**self.dynamodb["NewImage"])
        return None
    
    @property
    def old_image(self) -> Optional[DynamoDBImage]:
        """Get the old image from DynamoDB record"""
        if "OldImage" in self.dynamodb:
            return DynamoDBImage(**self.dynamodb["OldImage"])
        return None


class ProcessedRecord(BaseModel):
    """Processed DynamoDB record with parsed PK and SK"""
    pk: str
    sk: str
    event_name: EventName
    data: Dict[str, Any]
    
    @property
    def is_user_subscription(self) -> bool:
        """Check if this is a user subscription record"""
        return self.pk.startswith("USER#") and self.sk.startswith("SUB#")
    
    @property
    def is_user_profile(self) -> bool:
        """Check if this is a user profile record"""
        return self.pk.startswith("USER#") and self.sk == "PROFILE"
    
    @property
    def user_id(self) -> Optional[str]:
        """Extract user ID from PK"""
        if self.pk.startswith("USER#"):
            return self.pk.replace("USER#", "")
        return None
    
    @property
    def fund_id(self) -> Optional[str]:
        """Extract fund ID from SK for subscriptions"""
        if self.sk.startswith("SUB#"):
            return self.sk.replace("SUB#", "")
        return None