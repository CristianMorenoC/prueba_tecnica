from typing import Dict, Any, Optional, Union
from enum import Enum
from pydantic import BaseModel, Field


class EventName(str, Enum):
    INSERT = "INSERT"
    MODIFY = "MODIFY"
    REMOVE = "REMOVE"


class DynamoDBImage(BaseModel):
    """DynamoDB attribute value representation"""
    PK: Optional[Dict[str, Any]] = None
    SK: Optional[Dict[str, Any]] = None
    user_id: Optional[Dict[str, Any]] = None
    name: Optional[Dict[str, Any]] = None
    email: Optional[Dict[str, Any]] = None
    phone: Optional[Dict[str, Any]] = None
    balance: Optional[Dict[str, Any]] = None
    notification_channel: Optional[Dict[str, Any]] = None
    fund_id: Optional[Dict[str, Any]] = None
    amount: Optional[Dict[str, Any]] = None
    status: Optional[Dict[str, Any]] = None
    created_at: Optional[Dict[str, Any]] = None
    cancelled_at: Optional[Dict[str, Any]] = None


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
        """Extract user ID from data or PK as fallback"""
        # Try to get user_id from data first
        if "user_id" in self.data:
            return self.data["user_id"]
        # Fallback to extracting from PK
        if self.pk.startswith("USER#"):
            return self.pk.replace("USER#", "")
        return None
    
    @property
    def fund_id(self) -> Optional[str]:
        """Extract fund ID from data or SK as fallback"""
        # Try to get fund_id from data first
        if "fund_id" in self.data:
            return self.data["fund_id"]
        # Fallback to extracting from SK
        if self.sk.startswith("SUB#"):
            return self.sk.replace("SUB#", "")
        return None