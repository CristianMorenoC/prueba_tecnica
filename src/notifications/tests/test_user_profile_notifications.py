import pytest
from unittest.mock import AsyncMock, Mock
from application.use_cases.user_profile_notifications import UserProfileNotificationUseCase
from domain.models.dynamodb_record import ProcessedRecord, EventName
from domain.models.notification import NotificationChannel


@pytest.fixture
def mock_notification_sender():
    return AsyncMock()


@pytest.fixture
def mock_contact_manager():
    return AsyncMock()


@pytest.fixture
def user_profile_use_case(mock_notification_sender, mock_contact_manager):
    return UserProfileNotificationUseCase(mock_notification_sender, mock_contact_manager)


@pytest.fixture
def user_profile_insert_record():
    return ProcessedRecord(
        pk="USER#123",
        sk="PROFILE",
        event_name=EventName.INSERT,
        data={
            "user_id": "123",
            "email": "newuser@example.com",
            "phone": "+573001234567",
            "name": "New User",
            "notification_channel": "email",
            "balance": 0
        }
    )


@pytest.fixture
def user_profile_modify_record():
    return ProcessedRecord(
        pk="USER#123",
        sk="PROFILE",
        event_name=EventName.MODIFY,
        data={
            "user_id": "123",
            "email": "newuser@example.com",
            "name": "Updated User"
        }
    )


class TestUserProfileNotificationUseCase:
    
    @pytest.mark.asyncio
    async def test_handle_user_profile_creation_success(
        self, 
        user_profile_use_case,
        mock_notification_sender,
        mock_contact_manager,
        user_profile_insert_record
    ):
        """Test successful user profile creation handling"""
        mock_contact_manager.subscribe_email.return_value = "arn:aws:sns:us-east-1:123456789012:email:subscription-id"
        mock_contact_manager.subscribe_phone.return_value = "arn:aws:sns:us-east-1:123456789012:sms:subscription-id"
        mock_notification_sender.send_email.return_value = True
        
        result = await user_profile_use_case.handle_user_profile_creation(user_profile_insert_record)
        
        assert result is True
        mock_contact_manager.subscribe_email.assert_called_once_with("newuser@example.com")
        mock_contact_manager.subscribe_phone.assert_called_once_with("+573001234567")
        mock_notification_sender.send_email.assert_called_once()
        
        # Verify welcome email content
        call_args = mock_notification_sender.send_email.call_args[0][0]
        assert call_args.channel == NotificationChannel.EMAIL
        assert call_args.recipient == "newuser@example.com"
        assert "bienvenido" in call_args.subject.lower()
        assert "New User" in call_args.message
    
    @pytest.mark.asyncio
    async def test_handle_user_profile_creation_email_only(
        self, 
        user_profile_use_case,
        mock_notification_sender,
        mock_contact_manager
    ):
        """Test user profile creation with email only"""
        record = ProcessedRecord(
            pk="USER#123",
            sk="PROFILE",
            event_name=EventName.INSERT,
            data={
                "user_id": "123",
                "email": "emailonly@example.com",
                "name": "Email Only User",
                "notification_channel": "email"
            }
        )
        
        mock_contact_manager.subscribe_email.return_value = "email-subscription-arn"
        mock_notification_sender.send_email.return_value = True
        
        result = await user_profile_use_case.handle_user_profile_creation(record)
        
        assert result is True
        mock_contact_manager.subscribe_email.assert_called_once_with("emailonly@example.com")
        mock_contact_manager.subscribe_phone.assert_not_called()
        mock_notification_sender.send_email.assert_called_once()
    
    @pytest.mark.asyncio
    async def test_handle_user_profile_creation_phone_only(
        self, 
        user_profile_use_case,
        mock_notification_sender,
        mock_contact_manager
    ):
        """Test user profile creation with phone only"""
        record = ProcessedRecord(
            pk="USER#123",
            sk="PROFILE",
            event_name=EventName.INSERT,
            data={
                "user_id": "123",
                "phone": "+573009876543",
                "name": "Phone Only User",
                "notification_channel": "sms"
            }
        )
        
        mock_contact_manager.subscribe_phone.return_value = "phone-subscription-arn"
        
        result = await user_profile_use_case.handle_user_profile_creation(record)
        
        assert result is True
        mock_contact_manager.subscribe_phone.assert_called_once_with("+573009876543")
        mock_contact_manager.subscribe_email.assert_not_called()
        mock_notification_sender.send_email.assert_not_called()
    
    @pytest.mark.asyncio
    async def test_handle_non_profile_record(
        self, 
        user_profile_use_case,
        mock_notification_sender,
        mock_contact_manager
    ):
        """Test handling of non-profile record"""
        non_profile_record = ProcessedRecord(
            pk="USER#123",
            sk="SUB#fund456",
            event_name=EventName.INSERT,
            data={"fund_id": "fund456"}
        )
        
        result = await user_profile_use_case.handle_user_profile_creation(non_profile_record)
        
        assert result is False
        mock_contact_manager.subscribe_email.assert_not_called()
        mock_contact_manager.subscribe_phone.assert_not_called()
        mock_notification_sender.send_email.assert_not_called()
    
    @pytest.mark.asyncio
    async def test_handle_modify_event_ignored(
        self, 
        user_profile_use_case,
        mock_notification_sender,
        mock_contact_manager,
        user_profile_modify_record
    ):
        """Test that MODIFY events are ignored for user profiles"""
        result = await user_profile_use_case.handle_user_profile_creation(user_profile_modify_record)
        
        assert result is True  # Returns True but doesn't process
        mock_contact_manager.subscribe_email.assert_not_called()
        mock_contact_manager.subscribe_phone.assert_not_called()
        mock_notification_sender.send_email.assert_not_called()
    
    @pytest.mark.asyncio
    async def test_handle_missing_user_data(
        self, 
        user_profile_use_case,
        mock_notification_sender,
        mock_contact_manager
    ):
        """Test handling of record with missing user data"""
        incomplete_record = ProcessedRecord(
            pk="USER#123",
            sk="PROFILE",
            event_name=EventName.INSERT,
            data={}  # Missing user data
        )
        
        result = await user_profile_use_case.handle_user_profile_creation(incomplete_record)
        
        assert result is False
        mock_contact_manager.subscribe_email.assert_not_called()
        mock_contact_manager.subscribe_phone.assert_not_called()
        mock_notification_sender.send_email.assert_not_called()
    
    @pytest.mark.asyncio
    async def test_subscription_failure_handling(
        self, 
        user_profile_use_case,
        mock_notification_sender,
        mock_contact_manager,
        user_profile_insert_record
    ):
        """Test behavior when SNS subscription fails"""
        mock_contact_manager.subscribe_email.side_effect = Exception("SNS subscription failed")
        mock_contact_manager.subscribe_phone.return_value = "phone-subscription-arn"
        mock_notification_sender.send_email.return_value = True
        
        result = await user_profile_use_case.handle_user_profile_creation(user_profile_insert_record)
        
        assert result is False  # Should fail due to email subscription error
        mock_contact_manager.subscribe_email.assert_called_once()
        mock_contact_manager.subscribe_phone.assert_called_once()
        mock_notification_sender.send_email.assert_called_once()
    
    @pytest.mark.asyncio
    async def test_welcome_email_failure_handling(
        self, 
        user_profile_use_case,
        mock_notification_sender,
        mock_contact_manager,
        user_profile_insert_record
    ):
        """Test behavior when welcome email fails"""
        mock_contact_manager.subscribe_email.return_value = "email-subscription-arn"
        mock_contact_manager.subscribe_phone.return_value = "phone-subscription-arn"
        mock_notification_sender.send_email.side_effect = Exception("Email sending failed")
        
        result = await user_profile_use_case.handle_user_profile_creation(user_profile_insert_record)
        
        assert result is False  # Should fail due to email sending error
        mock_contact_manager.subscribe_email.assert_called_once()
        mock_contact_manager.subscribe_phone.assert_called_once()
        mock_notification_sender.send_email.assert_called_once()