import pytest
import sys
import os

# Add the src directory to the Python path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))

@pytest.fixture
def mock_aws_credentials(monkeypatch):
    """Mock AWS credentials for testing"""
    monkeypatch.setenv("AWS_ACCESS_KEY_ID", "testing")
    monkeypatch.setenv("AWS_SECRET_ACCESS_KEY", "testing")
    monkeypatch.setenv("AWS_SECURITY_TOKEN", "testing")
    monkeypatch.setenv("AWS_SESSION_TOKEN", "testing")
    monkeypatch.setenv("AWS_DEFAULT_REGION", "us-east-1")
    monkeypatch.setenv("EMAIL_TOPIC_ARN", "arn:aws:sns:us-east-1:123456789012:test-email-topic")
    monkeypatch.setenv("SMS_TOPIC_ARN", "arn:aws:sns:us-east-1:123456789012:test-sms-topic")