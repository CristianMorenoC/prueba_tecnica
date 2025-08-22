from fastapi import Depends
import os
import boto3
from functools import lru_cache

# Ports (Interfaces)
from app.application.ports.funds import FundPort
from app.application.ports.subscriptions import SubscriptionPort
from app.application.ports.transactions import TransactionPort
from app.application.ports.users import UserPort

# Adapters (Implementations)
from app.infrastructure.adapters.funds import FundAdapter
from app.infrastructure.adapters.subscription import SubscriptionAdapter
from app.infrastructure.adapters.transactions import TransactionAdapter
from app.infrastructure.adapters.users import UserAdapter

# Use Cases
from app.use_cases.subscriptions import SubscriptionUseCase
from app.use_cases.transactions import TransactionUseCase


@lru_cache()
def get_dynamodb_resource():
    """Create and cache DynamoDB resource connection."""
    return boto3.resource(
        'dynamodb',
        aws_access_key_id=os.getenv('AWS_ACCESS_KEY_ID'),
        aws_secret_access_key=os.getenv('AWS_SECRET_ACCESS_KEY'),
        region_name=os.getenv('AWS_DEFAULT_REGION', 'us-east-1')
    )


def get_fund_repository(
    dynamodb=Depends(get_dynamodb_resource)
) -> FundPort:
    """Factory for Fund repository - DynamoDB implementation."""
    return FundAdapter(dynamodb)


def get_subscription_repository(
    dynamodb=Depends(get_dynamodb_resource)
) -> SubscriptionPort:
    """Factory for Subscription repository - DynamoDB implementation."""
    return SubscriptionAdapter(dynamodb)


def get_transaction_repository(
    dynamodb=Depends(get_dynamodb_resource)
) -> TransactionPort:
    """Factory for Transaction repository - DynamoDB implementation."""
    return TransactionAdapter(dynamodb)


def get_user_repository(
    dynamodb=Depends(get_dynamodb_resource)
) -> UserPort:
    """Factory for User repository - DynamoDB implementation."""
    return UserAdapter(dynamodb)

# ============================================
# USE CASE FACTORIES
# ============================================


def get_subscription_use_case(
    fund_port: FundPort = Depends(get_fund_repository),
    subscription_port: SubscriptionPort = Depends(get_subscription_repository),
    transaction_port: TransactionPort = Depends(get_transaction_repository),
    user_port: UserPort = Depends(get_user_repository)
) -> SubscriptionUseCase:
    """Factory for Subscription use case with all dependencies injected."""
    return SubscriptionUseCase(
        funds_port=fund_port,
        subscription_port=subscription_port,
        transaction_port=transaction_port,
        user_port=user_port
    )


def get_transaction_use_case(
    transaction_port: TransactionPort = Depends(get_transaction_repository)
) -> TransactionUseCase:
    """Factory for Transaction use case with all dependencies injected."""
    return TransactionUseCase(transaction_port=transaction_port)
