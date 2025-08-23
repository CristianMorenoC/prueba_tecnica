import json
import logging
from typing import Dict, Any
import boto3
from botocore.exceptions import ClientError
from application.ports.notification_sender import NotificationSenderPort
from domain.models.notification import NotificationMessage, NotificationChannel
from config import EMAIL_TOPIC_ARN, SMS_TOPIC_ARN

logger = logging.getLogger(__name__)


class SNSNotificationSender(NotificationSenderPort):
    """SNS implementation for sending notifications"""
    
    def __init__(self):
        self.sns_client = boto3.client('sns')
        self.email_topic_arn = EMAIL_TOPIC_ARN
        self.sms_topic_arn = SMS_TOPIC_ARN
        
        # For local testing, allow None values but log warnings
        if not self.email_topic_arn:
            logger.warning("EMAIL_TOPIC_ARN not configured - email notifications will be disabled")
        if not self.sms_topic_arn:
            logger.warning("SMS_TOPIC_ARN not configured - SMS notifications will be disabled")
    
    async def send_email(self, message: NotificationMessage) -> bool:
        """
        Send email notification via SNS
        
        Args:
            message: NotificationMessage with email details
            
        Returns:
            bool: True if email was sent successfully
        """
        try:
            if message.channel != NotificationChannel.EMAIL:
                logger.error(f"Invalid channel for email: {message.channel}")
                return False
            
            if not self.email_topic_arn:
                logger.warning("EMAIL_TOPIC_ARN not configured - skipping email notification")
                return True  # Return True for local testing
            
            # Create message structure for email
            email_message = {
                "default": message.message,
                "email": json.dumps({
                    "Subject": message.subject,
                    "Message": message.message
                })
            }
            
            # Extract user_id from metadata for filtering
            user_id = message.metadata.get('user_id', 'unknown')
            
            # Publish to SNS topic
            response = self.sns_client.publish(
                TopicArn=self.email_topic_arn,
                Message=json.dumps(email_message),
                Subject=message.subject,
                MessageStructure='json',
                MessageAttributes={
                    'user_id': {
                        'DataType': 'String',
                        'StringValue': user_id
                    }
                }
            )
            
            logger.info(f"Email notification sent successfully. MessageId: {response['MessageId']}")
            return True
            
        except ClientError as e:
            logger.error(f"AWS SNS error sending email: {str(e)}")
            return False
        except Exception as e:
            logger.error(f"Unexpected error sending email: {str(e)}")
            return False
    
    async def send_sms(self, message: NotificationMessage) -> bool:
        """
        Send SMS notification via SNS
        
        Args:
            message: NotificationMessage with SMS details
            
        Returns:
            bool: True if SMS was sent successfully
        """
        try:
            if message.channel != NotificationChannel.SMS:
                logger.error(f"Invalid channel for SMS: {message.channel}")
                return False
            
            if not self.sms_topic_arn:
                logger.warning("SMS_TOPIC_ARN not configured - skipping SMS notification")
                return True  # Return True for local testing
            
            # For SMS, we send directly to the phone number
            # First check if phone number is subscribed to SMS topic
            sms_message = f"{message.subject}: {message.message}"
            
            # Extract user_id from metadata for filtering
            user_id = message.metadata.get('user_id', 'unknown')
            
            # For SMS, publish to topic instead of direct phone number to use filtering
            response = self.sns_client.publish(
                TopicArn=self.sms_topic_arn,
                Message=sms_message,
                MessageAttributes={
                    'user_id': {
                        'DataType': 'String',
                        'StringValue': user_id
                    },
                    'notification_type': {
                        'DataType': 'String',
                        'StringValue': message.type.value
                    },
                    'AWS.SNS.SMS.SenderID': {
                        'DataType': 'String',
                        'StringValue': 'Amaris'
                    },
                    'AWS.SNS.SMS.SMSType': {
                        'DataType': 'String',
                        'StringValue': 'Transactional'
                    }
                }
            )
            
            logger.info(f"SMS notification sent successfully. MessageId: {response['MessageId']}")
            return True
            
        except ClientError as e:
            logger.error(f"AWS SNS error sending SMS: {str(e)}")
            return False
        except Exception as e:
            logger.error(f"Unexpected error sending SMS: {str(e)}")
            return False
    
    def _format_phone_number(self, phone: str) -> str:
        """Format phone number for SNS"""
        # Remove any non-digit characters
        phone_digits = ''.join(filter(str.isdigit, phone))
        
        # Add country code if not present (assuming +57 for Colombia)
        if not phone_digits.startswith('57') and len(phone_digits) == 10:
            phone_digits = '57' + phone_digits
        
        return '+' + phone_digits