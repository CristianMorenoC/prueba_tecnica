import logging
from typing import Dict, Any
from domain.models.dynamodb_record import ProcessedRecord, EventName
from domain.models.notification import (
    SubscriptionNotification, 
    NotificationChannel,
    NotificationType
)
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
            
            # Send notifications based on user's preferred channels
            success = True
            
            if user_data.get("notify_channel") == "email" and user_data.get("email"):
                email_notification = self._create_email_notification(
                    record, user_data, notification_type
                )
                email_success = await self.notification_sender.send_email(email_notification)
                success = success and email_success
                logger.info(f"Email notification sent: {email_success}")
            
            if user_data.get("notify_channel") == "sms" and user_data.get("phone"):
                sms_notification = self._create_sms_notification(
                    record, user_data, notification_type
                )
                sms_success = await self.notification_sender.send_sms(sms_notification)
                success = success and sms_success
                logger.info(f"SMS notification sent: {sms_success}")
            
            return success
            
        except Exception as e:
            logger.error(f"Error handling subscription notification: {str(e)}")
            return False
    
    def _extract_user_data(self, data: Dict[str, Any]) -> Dict[str, Any]:
        """Extract user data from record data"""
        user_data = {
            "email": data.get("email"),
            "phone": data.get("phone"),
            "notify_channel": data.get("notify_channel"),
            "name": data.get("name", "Usuario")
        }
        
        logger.info(f"Extracted user data: {user_data}")
        
        # For subscription events, we might not have email/phone in the record
        # This is expected behavior - skip notification if no contact info
        if not user_data.get("email") and not user_data.get("phone"):
            logger.warning("No email or phone found in subscription record - cannot send notification")
            return None
            
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
    
    def _create_email_notification(
        self, 
        record: ProcessedRecord, 
        user_data: Dict[str, Any], 
        notification_type: str
    ) -> SubscriptionNotification:
        """Create email notification for subscription"""
        if notification_type == NotificationType.SUBSCRIPTION_CREATED:
            subject = f"Suscripción Creada - Fondo {record.fund_id}"
            message = f"Hola {user_data['name']}, tu suscripción al fondo {record.fund_id} ha sido creada exitosamente."
        else:
            subject = f"Suscripción Cancelada - Fondo {record.fund_id}"
            message = f"Hola {user_data['name']}, tu suscripción al fondo {record.fund_id} ha sido cancelada."
        
        return SubscriptionNotification(
            type=notification_type,  # Determinado por la lambda basado en el evento
            channel=NotificationChannel.EMAIL,
            recipient=user_data["email"],
            subject=subject,
            message=message,
            user_id=record.user_id,
            fund_id=record.fund_id,
            metadata={
                "user_id": record.user_id,  # Para filtrado SNS
                "event_name": record.event_name.value,
                "subscription_data": record.data
            }
        )
    
    def _create_sms_notification(
        self, 
        record: ProcessedRecord, 
        user_data: Dict[str, Any], 
        notification_type: str
    ) -> SubscriptionNotification:
        """Create SMS notification for subscription"""
        if notification_type == NotificationType.SUBSCRIPTION_CREATED:
            subject = "Suscripción Creada"
            message = f"Tu suscripción al fondo {record.fund_id} ha sido creada."
        else:
            subject = "Suscripción Cancelada"
            message = f"Tu suscripción al fondo {record.fund_id} ha sido cancelada."
        
        return SubscriptionNotification(
            type=notification_type,  # Determinado por la lambda basado en el evento
            channel=NotificationChannel.SMS,
            recipient=user_data["phone"],
            subject=subject,
            message=message,
            user_id=record.user_id,
            fund_id=record.fund_id,
            metadata={
                "user_id": record.user_id,  # Para filtrado SNS
                "event_name": record.event_name.value,
                "subscription_data": record.data
            }
        )