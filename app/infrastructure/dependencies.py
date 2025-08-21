from fastapi import Depends

from app.application.ports.funds import FundPort
from app.application.ports.subscriptions import SubscriptionPort
from app.application.ports.transactions import TransactionPort
from app.infrastructure.adapters.funds import FundAdapter
from app.infrastructure.adapters.subscription import SubscriptionAdapter
from app.infrastructure.adapters.transactions import TransactionAdapter
from app.use_cases.subscriptions import SubscriptionUseCase
from app.use_cases.transactions import TransactionUseCase


def get_fund_repository() -> FundPort:
    """Factory for Fund repository."""
    return FundAdapter()


def get_subscription_repository() -> SubscriptionPort:
    """Factory for Subscription repository."""
    return SubscriptionAdapter()


def get_transaction_repository() -> TransactionPort:
    """Factory for Transaction repository."""
    return TransactionAdapter()


def get_subscription_use_case(
    fund_port: FundPort = Depends(get_fund_repository),
    subscription_port: SubscriptionPort = Depends(get_subscription_repository)
) -> SubscriptionUseCase:
    """Factory for Subscription use case with all dependencies injected."""
    return SubscriptionUseCase(
        funds_port=fund_port,
        subscription_port=subscription_port
    )


def get_transaction_use_case(
    transaction_port: TransactionPort = Depends(get_transaction_repository)
) -> TransactionUseCase:
    """Factory for Transaction use case with all dependencies injected."""
    return TransactionUseCase(transaction_port=transaction_port)
