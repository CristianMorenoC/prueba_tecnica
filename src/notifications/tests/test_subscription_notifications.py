import pytest
from unittest.mock import AsyncMock, Mock
from application.use_cases.subscription_notifications import SubscriptionNotificationUseCase
from domain.models.dynamodb_record import ProcessedRecord, EventName
from domain.models.notification import NotificationChannel


@pytest.fixture
def mock_notification_sender():
    return AsyncMock()


@pytest.fixture
def subscription_use_case(mock_notification_sender):
    return SubscriptionNotificationUseCase(mock_notification_sender)


@pytest.fixture
def subscription_insert_record():
    return ProcessedRecord(
        pk="USER#123",
        sk="SUB#fund456",
        event_name=EventName.INSERT,
        data={
            "user_id": "123",
            "fund_id": "fund456",
            "email": "test@example.com",
            "phone": "+573001234567",
            "name": "Test User",
            "notification_channel": "email",
            "amount": 10000,
            "status": "active"
        }
    )


@pytest.fixture
def subscription_modify_cancelled_record():
    return ProcessedRecord(
        pk="USER#123",
        sk="SUB#fund456",
        event_name=EventName.MODIFY,
        data={
            "user_id": "123",
            "fund_id": "fund456",
            "email": "test@example.com",
            "phone": "+573001234567",
            "name": "Test User",
            "notification_channel": "sms",
            "amount": 10000,
            "status": "cancelled"
        }
    )


class TestSubscriptionNotificationUseCase:
    
    @pytest.mark.asyncio
    async def test_handle_subscription_creation_email(
        self, 
        subscription_use_case, 
        mock_notification_sender,
        subscription_insert_record
    ):
        """Test subscription creation notification via email"""
        mock_notification_sender.send_email.return_value = True
        
        result = await subscription_use_case.handle_subscription_change(subscription_insert_record)
        
        assert result is True
        mock_notification_sender.send_email.assert_called_once()
        
        # Verify email notification content
        call_args = mock_notification_sender.send_email.call_args[0][0]
        assert call_args.channel == NotificationChannel.EMAIL
        assert call_args.recipient == "test@example.com"
        assert "fund456" in call_args.subject
        assert "creada" in call_args.subject.lower()
    
    @pytest.mark.asyncio
    async def test_handle_subscription_cancellation_sms(
        self, 
        subscription_use_case, 
        mock_notification_sender,
        subscription_modify_cancelled_record
    ):
        """Test subscription cancellation notification via SMS"""
        mock_notification_sender.send_sms.return_value = True
        
        result = await subscription_use_case.handle_subscription_change(subscription_modify_cancelled_record)
        
        assert result is True
        mock_notification_sender.send_sms.assert_called_once()
        
        # Verify SMS notification content
        call_args = mock_notification_sender.send_sms.call_args[0][0]
        assert call_args.channel == NotificationChannel.SMS
        assert call_args.recipient == "+573001234567"
        assert "fund456" in call_args.subject
        assert "cancelada" in call_args.subject.lower()
    
    @pytest.mark.asyncio
    async def test_handle_non_subscription_record(
        self, 
        subscription_use_case,
        mock_notification_sender
    ):
        """Test handling of non-subscription record"""
        non_subscription_record = ProcessedRecord(
            pk="USER#123",
            sk="PROFILE",
            event_name=EventName.INSERT,
            data={"name": "Test User"}
        )
        
        result = await subscription_use_case.handle_subscription_change(non_subscription_record)
        
        assert result is False
        mock_notification_sender.send_email.assert_not_called()
        mock_notification_sender.send_sms.assert_not_called()
    
    @pytest.mark.asyncio
    async def test_handle_missing_user_data(
        self, 
        subscription_use_case,
        mock_notification_sender
    ):
        """Test handling of record with missing user data"""
        incomplete_record = ProcessedRecord(
            pk="USER#123",
            sk="SUB#fund456",
            event_name=EventName.INSERT,
            data={}  # Missing user data
        )
        
        result = await subscription_use_case.handle_subscription_change(incomplete_record)
        
        assert result is False
        mock_notification_sender.send_email.assert_not_called()
        mock_notification_sender.send_sms.assert_not_called()
    
    @pytest.mark.asyncio
    async def test_notification_sender_failure(
        self, 
        subscription_use_case,
        mock_notification_sender,
        subscription_insert_record
    ):
        """Test behavior when notification sending fails"""
        mock_notification_sender.send_email.return_value = False
        
        result = await subscription_use_case.handle_subscription_change(subscription_insert_record)
        
        assert result is False
        mock_notification_sender.send_email.assert_called_once()
    
    @pytest.mark.asyncio
    async def test_modify_event_without_cancellation(
        self, 
        subscription_use_case,
        mock_notification_sender
    ):
        """Test MODIFY event that doesn't involve cancellation"""
        modify_record = ProcessedRecord(
            pk="USER#123",
            sk="SUB#fund456",
            event_name=EventName.MODIFY,
            data={
                "user_id": "123",
                "fund_id": "fund456",
                "email": "test@example.com",
                "name": "Test User",
                "notification_channel": "email",
                "status": "active"  # Still active, not cancelled
            }
        )
        
        result = await subscription_use_case.handle_subscription_change(modify_record)
        
        assert result is True  # No notification needed, but no error
        mock_notification_sender.send_email.assert_not_called()
        mock_notification_sender.send_sms.assert_not_called()