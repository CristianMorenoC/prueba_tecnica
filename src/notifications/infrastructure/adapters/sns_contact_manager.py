import logging
from typing import Optional
import boto3
from botocore.exceptions import ClientError
from application.ports.notification_sender import ContactManagerPort
from config import EMAIL_TOPIC_ARN, SMS_TOPIC_ARN

logger = logging.getLogger(__name__)


class SNSContactManager(ContactManagerPort):
    """SNS implementation for managing contact subscriptions"""
    
    def __init__(self):
        self.sns_client = boto3.client('sns')
        self.email_topic_arn = EMAIL_TOPIC_ARN
        self.sms_topic_arn = SMS_TOPIC_ARN
        
        # For local testing, allow None values but log warnings
        if not self.email_topic_arn:
            logger.warning("EMAIL_TOPIC_ARN not configured - email subscriptions will be disabled")
        if not self.sms_topic_arn:
            logger.warning("SMS_TOPIC_ARN not configured - SMS subscriptions will be disabled")
    
    async def subscribe_email(self, email: str, user_id: str) -> str:
        """
        Subscribe email address to SNS email topic with user_id filter
        
        Args:
            email: Email address to subscribe
            user_id: User ID for message filtering
            
        Returns:
            str: Subscription ARN
        """
        try:
            if not self.email_topic_arn:
                logger.warning("EMAIL_TOPIC_ARN not configured - skipping email subscription")
                return "local-test-subscription-arn-email"
            
            logger.info(f"Subscribing email to SNS topic: {email} for user: {user_id}")
            
            response = self.sns_client.subscribe(
                TopicArn=self.email_topic_arn,
                Protocol='email',
                Endpoint=email,
                Attributes={
                    'FilterPolicy': f'{{"user_id": ["{user_id}"]}}'
                }
            )
            
            subscription_arn = response['SubscriptionArn']
            logger.info(f"Email subscription created: {email} -> {subscription_arn} (user: {user_id})")
            
            return subscription_arn
            
        except ClientError as e:
            logger.error(f"AWS SNS error subscribing email {email}: {str(e)}")
            raise
        except Exception as e:
            logger.error(f"Unexpected error subscribing email {email}: {str(e)}")
            raise
    
    async def subscribe_phone(self, phone: str, user_id: str) -> str:
        """
        Subscribe phone number to SNS SMS topic with user_id filter
        
        Args:
            phone: Phone number to subscribe
            user_id: User ID for message filtering
            
        Returns:
            str: Subscription ARN
        """
        try:
            if not self.sms_topic_arn:
                logger.warning("SMS_TOPIC_ARN not configured - skipping SMS subscription")
                return "local-test-subscription-arn-sms"
                
            formatted_phone = self._format_phone_number(phone)
            logger.info(f"Subscribing phone to SNS topic: {formatted_phone} for user: {user_id}")
            
            response = self.sns_client.subscribe(
                TopicArn=self.sms_topic_arn,
                Protocol='sms',
                Endpoint=formatted_phone,
                Attributes={
                    'FilterPolicy': f'{{"user_id": ["{user_id}"]}}'
                }
            )
            
            subscription_arn = response['SubscriptionArn']
            logger.info(f"Phone subscription created: {formatted_phone} -> {subscription_arn} (user: {user_id})")
            
            return subscription_arn
            
        except ClientError as e:
            logger.error(f"AWS SNS error subscribing phone {phone}: {str(e)}")
            raise
        except Exception as e:
            logger.error(f"Unexpected error subscribing phone {phone}: {str(e)}")
            raise
    
    async def unsubscribe(self, subscription_arn: str) -> bool:
        """
        Unsubscribe from SNS topic
        
        Args:
            subscription_arn: ARN of the subscription to remove
            
        Returns:
            bool: True if unsubscribed successfully
        """
        try:
            logger.info(f"Unsubscribing from SNS: {subscription_arn}")
            
            self.sns_client.unsubscribe(
                SubscriptionArn=subscription_arn
            )
            
            logger.info(f"Successfully unsubscribed: {subscription_arn}")
            return True
            
        except ClientError as e:
            logger.error(f"AWS SNS error unsubscribing {subscription_arn}: {str(e)}")
            return False
        except Exception as e:
            logger.error(f"Unexpected error unsubscribing {subscription_arn}: {str(e)}")
            return False
    
    def _format_phone_number(self, phone: str) -> str:
        """Format phone number for SNS"""
        # Remove any non-digit characters
        phone_digits = ''.join(filter(str.isdigit, phone))
        
        # Add country code if not present (assuming +57 for Colombia)
        if not phone_digits.startswith('57') and len(phone_digits) == 10:
            phone_digits = '57' + phone_digits
        
        return '+' + phone_digits
    
    async def list_subscriptions_by_topic(self, topic_arn: str) -> list:
        """
        List all subscriptions for a topic (helper method for debugging)
        
        Args:
            topic_arn: SNS topic ARN
            
        Returns:
            list: List of subscriptions
        """
        try:
            response = self.sns_client.list_subscriptions_by_topic(
                TopicArn=topic_arn
            )
            return response.get('Subscriptions', [])
        except Exception as e:
            logger.error(f"Error listing subscriptions for topic {topic_arn}: {str(e)}")
            return []