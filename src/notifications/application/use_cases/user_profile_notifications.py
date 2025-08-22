import logging
from typing import Dict, Any
from domain.models.dynamodb_record import ProcessedRecord, EventName
from domain.models.notification import (
    UserProfileNotification, 
    NotificationChannel,
    NotificationType
)
from application.ports.notification_sender import NotificationSenderPort
from application.ports.notification_sender import ContactManagerPort

logger = logging.getLogger(__name__)


class UserProfileNotificationUseCase:
    """Use case for handling user profile creation notifications"""
    
    def __init__(
        self, 
        notification_sender: NotificationSenderPort,
        contact_manager: ContactManagerPort
    ):
        self.notification_sender = notification_sender
        self.contact_manager = contact_manager
    
    async def handle_user_profile_creation(self, record: ProcessedRecord) -> bool:
        """
        Handle user profile creation and set up SNS subscriptions
        
        Args:
            record: ProcessedRecord for USER#{id_user} / PROFILE
            
        Returns:
            bool: True if profile was processed successfully
        """
        try:
            if not record.is_user_profile:
                logger.warning(f"Record is not a user profile: PK={record.pk}, SK={record.sk}")
                return False
            
            if record.event_name != EventName.INSERT:
                logger.info(f"Ignoring non-INSERT event for user profile: {record.event_name}")
                return True
            
            user_data = self._extract_user_data(record.data)
            if not user_data:
                logger.error(f"Could not extract user data from record: {record.data}")
                return False
            
            # Subscribe user to SNS topics
            success = True
            
            # Subscribe email if provided
            if user_data.get("email"):
                try:
                    email_subscription_arn = await self.contact_manager.subscribe_email(
                        user_data["email"]
                    )
                    logger.info(f"Email subscribed: {user_data['email']} -> {email_subscription_arn}")
                except Exception as e:
                    logger.error(f"Failed to subscribe email {user_data['email']}: {str(e)}")
                    success = False
            
            # Subscribe phone if provided
            if user_data.get("phone"):
                try:
                    phone_subscription_arn = await self.contact_manager.subscribe_phone(
                        user_data["phone"]
                    )
                    logger.info(f"Phone subscribed: {user_data['phone']} -> {phone_subscription_arn}")
                except Exception as e:
                    logger.error(f"Failed to subscribe phone {user_data['phone']}: {str(e)}")
                    success = False
            
            # Send welcome notification if email is available
            if user_data.get("email"):
                try:
                    welcome_notification = self._create_welcome_notification(record, user_data)
                    await self.notification_sender.send_email(welcome_notification)
                    logger.info(f"Welcome email sent to: {user_data['email']}")
                except Exception as e:
                    logger.error(f"Failed to send welcome email: {str(e)}")
                    success = False
            
            return success
            
        except Exception as e:
            logger.error(f"Error handling user profile creation: {str(e)}")
            return False
    
    def _extract_user_data(self, data: Dict[str, Any]) -> Dict[str, Any]:
        """Extract user data from record data"""
        return {
            "email": data.get("email"),
            "phone": data.get("phone"),
            "name": data.get("name", "Usuario"),
            "notify_channel": data.get("notify_channel", "email")
        }
    
    def _create_welcome_notification(
        self, 
        record: ProcessedRecord, 
        user_data: Dict[str, Any]
    ) -> UserProfileNotification:
        """Create welcome notification for new user"""
        subject = "Bienvenido a Amaris - Perfil Creado"
        message = f"""
        ¡Hola {user_data['name']}!
        
        Tu perfil en Amaris ha sido creado exitosamente. Ya puedes comenzar a gestionar tus suscripciones a fondos.
        
        Datos de tu perfil:
        - Email: {user_data.get('email', 'No proporcionado')}
        - Teléfono: {user_data.get('phone', 'No proporcionado')}
        - Canal de notificaciones: {user_data.get('notify_channel', 'email')}
        
        ¡Gracias por unirte a nosotros!
        
        Equipo Amaris
        """
        
        return UserProfileNotification(
            type=NotificationType.USER_PROFILE_CREATED,  # Determinado por la lambda
            channel=NotificationChannel.EMAIL,
            recipient=user_data["email"],
            subject=subject,
            message=message,
            user_id=record.user_id,
            metadata={
                "event_name": record.event_name.value,
                "user_data": user_data
            }
        )