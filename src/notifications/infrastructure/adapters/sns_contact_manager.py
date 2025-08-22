import logging
import os
from typing import Optional
import boto3
from botocore.exceptions import ClientError
from application.ports.notification_sender import ContactManagerPort

logger = logging.getLogger(__name__)


class SNSContactManager(ContactManagerPort):
    """SNS implementation for managing contact subscriptions"""
    
    def __init__(self):
        self.sns_client = boto3.client('sns')
        self.email_topic_arn = os.environ.get('EMAIL_TOPIC_ARN')
        self.sms_topic_arn = os.environ.get('SMS_TOPIC_ARN')
        
        if not self.email_topic_arn:
            raise ValueError("EMAIL_TOPIC_ARN environment variable is required")
        if not self.sms_topic_arn:
            raise ValueError("SMS_TOPIC_ARN environment variable is required")
    
    async def subscribe_email(self, email: str) -> str:
        """
        Subscribe email address to SNS email topic
        
        Args:
            email: Email address to subscribe
            
        Returns:
            str: Subscription ARN
        """
        try:
            logger.info(f"Subscribing email to SNS topic: {email}")
            
            response = self.sns_client.subscribe(
                TopicArn=self.email_topic_arn,
                Protocol='email',
                Endpoint=email
            )
            
            subscription_arn = response['SubscriptionArn']
            logger.info(f"Email subscription created: {email} -> {subscription_arn}")
            
            return subscription_arn
            
        except ClientError as e:
            logger.error(f"AWS SNS error subscribing email {email}: {str(e)}")
            raise
        except Exception as e:
            logger.error(f"Unexpected error subscribing email {email}: {str(e)}")
            raise
    
    async def subscribe_phone(self, phone: str) -> str:
        """
        Subscribe phone number to SNS SMS topic
        
        Args:
            phone: Phone number to subscribe
            
        Returns:
            str: Subscription ARN
        """
        try:
            formatted_phone = self._format_phone_number(phone)
            logger.info(f"Subscribing phone to SNS topic: {formatted_phone}")
            
            response = self.sns_client.subscribe(
                TopicArn=self.sms_topic_arn,
                Protocol='sms',
                Endpoint=formatted_phone
            )
            
            subscription_arn = response['SubscriptionArn']
            logger.info(f"Phone subscription created: {formatted_phone} -> {subscription_arn}")
            
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