"""
Configuración común para tests de use cases.
"""
import pytest
from unittest.mock import Mock

from ..domain.models.user import User, NotifyChannel
from ..domain.models.fund import Fund
from ..domain.models.subscription import Subscription, Status


@pytest.fixture
def default_user():
    """Usuario con balance inicial estándar de COP $500.000."""
    return User(
        user_id="u001",
        name="Test User",
        email="test@example.com",
        balance=500000,
        notify_channel=NotifyChannel.EMAIL,
        phone="+1-234-567-8900"
    )


@pytest.fixture
def low_balance_user():
    """Usuario con saldo insuficiente para algunas operaciones."""
    return User(
        user_id="u002", 
        name="Low Balance User",
        email="lowbalance@example.com",
        balance=30000,
        notify_channel=NotifyChannel.SMS,
        phone="+1-234-567-8901"
    )


@pytest.fixture
def basic_fund():
    """Fondo básico con monto mínimo estándar."""
    return Fund(
        fund_id="f001",
        name="Fondo Básico",
        min_amount=50000,
        category="FPV"
    )


@pytest.fixture
def premium_fund():
    """Fondo premium con monto mínimo alto."""
    return Fund(
        fund_id="f002",
        name="Fondo Premium",
        min_amount=200000,
        category="FIC"
    )


@pytest.fixture
def active_subscription():
    """Suscripción activa estándar."""
    return Subscription(
        user_id="u001",
        fund_id="f001",
        amount=100000,
        status=Status.ACTIVE,
        created_at="2025-08-22T10:00:00Z"
    )


@pytest.fixture
def cancelled_subscription():
    """Suscripción cancelada."""
    return Subscription(
        user_id="u001",
        fund_id="f001",
        amount=100000,
        status=Status.CANCELLED,
        created_at="2025-08-22T10:00:00Z",
        cancelled_at="2025-08-22T11:00:00Z"
    )


@pytest.fixture
def mock_funds_port():
    """Mock del puerto de fondos."""
    return Mock()


@pytest.fixture
def mock_subscription_port():
    """Mock del puerto de suscripciones."""
    return Mock()


@pytest.fixture
def mock_transaction_port():
    """Mock del puerto de transacciones."""
    return Mock()


@pytest.fixture
def mock_user_port():
    """Mock del puerto de usuarios."""
    return Mock()


@pytest.fixture
def subscription_use_case(
    mock_funds_port,
    mock_subscription_port, 
    mock_transaction_port,
    mock_user_port
):
    """Instancia del caso de uso con todos los mocks inyectados."""
    from ..use_cases.subscriptions import SubscriptionUseCase

    return SubscriptionUseCase(
        funds_port=mock_funds_port,
        subscription_port=mock_subscription_port,
        transaction_port=mock_transaction_port,
        user_port=mock_user_port
    )
