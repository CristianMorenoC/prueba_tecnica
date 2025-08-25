import logging
from typing import Dict, Any
from domain.models.dynamodb_record import ProcessedRecord, EventName
from domain.models.notification import (
    SubscriptionNotification, 
    NotificationChannel,
    NotificationType
)
from domain.models.notification import NotificationMessage
from application.ports.notification_sender import NotificationSenderPort

logger = logging.getLogger(__name__)


class SubscriptionNotificationUseCase:
    """Use case for handling subscription-related notifications"""
    
    def __init__(self, notification_sender: NotificationSenderPort):
        self.notification_sender = notification_sender
    
    async def handle_subscription_change(self, record: ProcessedRecord) -> bool:
        """
        Handle subscription changes and send appropriate notifications
        
        Args:
            record: ProcessedRecord for USER#{id_user} / SUB#{id_fondo}
            
        Returns:
            bool: True if notification was sent successfully
        """
        try:
            if not record.is_user_subscription:
                logger.warning(f"Record is not a subscription: PK={record.pk}, SK={record.sk}")
                return False
            
            user_data = self._extract_user_data(record.data)
            if not user_data:
                logger.info(f"No user contact data available for subscription notification - skipping")
                return True  # Return True because this is not an error, just no notification needed
            
            # Determine notification type based on event and status
            notification_type = self._determine_notification_type(record)
            if not notification_type:
                logger.info(f"No notification needed for event: {record.event_name}")
                return True
            
            # For subscription events, we just log the event since we don't have user contact info
            # The actual notifications are sent when user profiles are created
            logger.info(f"Subscription event processed: {notification_type} for user {record.user_id}, fund {record.fund_id}")
            logger.info(f"Preferred notification channel: {user_data.get('notificationChannel', 'not specified')}")
            
            # Return True since the subscription event was processed successfully
            # Convert string channel to enum
            logger.info(f"DEBUG - Raw record.data: {record.data}")
            logger.info(f"DEBUG - user_data: {user_data}")
            channel_str = user_data.get("notificationChannel")
            logger.info(f"DEBUG - channel_str: {channel_str} (type: {type(channel_str)})")
            channel_enum = channel_str if channel_str else NotificationChannel.EMAIL
            logger.info(f"DEBUG - channel_enum: {channel_enum}")
            
            message = NotificationMessage(
                type=notification_type,
                channel=channel_enum,
                subject=f"Subscription Update for Fund {record.fund_id}",
                message=f"Your subscription to fund  has been successful .",
                metadata=record.data
            )
            await self.notification_sender.send_email(message)
            return True
            
        except Exception as e:
            logger.error(f"Error handling subscription notification: {str(e)}")
            return False
    
    def _extract_user_data(self, data: Dict[str, Any]) -> Dict[str, Any]:
        """Extract user data from record data"""
        user_data = {
            "notificationChannel": data.get("notificationChannel")
        }
        
        logger.info(f"Extracted user data: {user_data}")
        return user_data
    
    def _determine_notification_type(self, record: ProcessedRecord) -> str:
        """Determine notification type based on record"""
        if record.event_name == EventName.INSERT:
            return NotificationType.SUBSCRIPTION_CREATED
        elif record.event_name == EventName.MODIFY:
            # Check if status changed to cancelled
            status = record.data.get("status")
            if status == "cancelled":
                return NotificationType.SUBSCRIPTION_CANCELLED
        return None
    
