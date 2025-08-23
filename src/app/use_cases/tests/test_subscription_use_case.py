import pytest
from unittest.mock import Mock

from use_cases.subscriptions import SubscriptionUseCase
from domain.models.user import User, NotifyChannel
from domain.models.fund import Fund
from domain.models.subscription import Subscription, Status
from domain.models.transaction import TransactionType


class TestSubscriptionUseCaseBusinessRules:
    """
    Tests para verificar las reglas de negocio del sistema de suscripciones.
    """

    def setup_method(self):
        """Setup para cada test - crea mocks de todos los puertos."""
        self.funds_port = Mock()
        self.subscription_port = Mock()
        self.transaction_port = Mock()
        self.user_port = Mock()

        self.use_case = SubscriptionUseCase(
            funds_port=self.funds_port,
            subscription_port=self.subscription_port,
            transaction_port=self.transaction_port,
            user_port=self.user_port
        )

    def test_minimum_fund_amount_validation(self):
        """
        Regla de negocio: Cada fondo tiene un monto mínimo de vinculación.
        El sistema debe rechazar suscripciones por debajo del monto mínimo.
        """
        # Arrange
        user = User(
            user_id="u001",
            name="Test User",
            email="test@example.com",
            balance=500000,
            notify_channel=NotifyChannel.EMAIL,
            phone="+1-234-567-8900"
        )

        fund = Fund(
            fund_id="f001",
            name="Fondo Premium",
            min_amount=100000,
            category="FPV"
        )

        self.funds_port.get_by_id.return_value = fund
        self.user_port.get_by_id.return_value = user

        # Act & Assert
        with pytest.raises(
            ValueError,
            match="No tiene saldo disponible para vincularse al fondo"
        ):
            # Intentar suscribirse con monto menor al mínimo
            self.use_case.subscribe(
                fund_id="f001",
                user_id=user.user_id,
                amount=50000,
                notification_channel="email"
            )

        # Verificar que no se realizaron operaciones
        self.subscription_port.save.assert_not_called()
        self.transaction_port.save.assert_not_called()

    def test_insufficient_balance_shows_specific_message(self):
        """
        Regla de negocio: Si no hay saldo suficiente, mostrar mensaje
        específico con el nombre del fondo.
        """
        # Arrange
        user = User(
            user_id="u001",
            name="Test User",
            email="test@example.com",
            balance=80000,
            notify_channel=NotifyChannel.EMAIL,
            phone="+1-234-567-8900"
        )

        fund = Fund(
            fund_id="f001",
            name="Fondo de Inversión Premium",
            min_amount=50000,
            category="FPV"
        )

        self.funds_port.get_by_id.return_value = fund
        self.user_port.get_by_id.return_value = user

        # Act & Assert
        with pytest.raises(ValueError) as exc_info:
            self.use_case.subscribe(
                fund_id="f001",
                user_id=user.user_id,
                amount=100000,
                notification_channel="email"
            )

        # Verificar mensaje específico con nombre del fondo
        assert ("No hay suficiente saldo para vincularse "
                "al fondo $Fondo de Inversión Premium" in str(exc_info.value))

    def test_successful_subscription_creates_transaction_with_unique_id(self):
        """
        Reglas de negocio:
        1. Cada transacción debe tener un identificador único
        2. Se debe actualizar el saldo del usuario
        3. Se debe crear una suscripción activa
        """
        # Arrange
        user = User(
            user_id="u001",
            name="Test User",
            email="test@example.com",
            balance=500000,
            notify_channel=NotifyChannel.EMAIL,
            phone="+1-234-567-8900"
        )

        fund = Fund(
            fund_id="f001",
            name="Fondo Básico",
            min_amount=50000.0,
            category="FPV"
        )

        expected_subscription = Subscription(
            user_id="u001",
            fund_id="f001",
            amount=100000,
            status=Status.ACTIVE
        )

        self.funds_port.get_by_id.return_value = fund
        self.user_port.get_by_id.return_value = user
        self.subscription_port.save.return_value = expected_subscription
        self.user_port.get_by_id.return_value = user
        self.user_port.update.return_value = user

        # Act
        result = self.use_case.subscribe(
            fund_id="f001",
            user_id=user.user_id,
            amount=100000,
            notification_channel="email"
        )

        # Assert
        # Verificar que se actualizó el saldo del usuario
        self.user_port.update.assert_called_once_with(
            "u001",
            new_balance=400000  # 500000 - 100000
        )

        # Verificar que se guardó la suscripción
        self.subscription_port.save.assert_called_once()
        saved_subscription = self.subscription_port.save.call_args[0][0]
        assert saved_subscription.user_id == "u001"
        assert saved_subscription.fund_id == "f001"
        assert saved_subscription.amount == 100000
        assert saved_subscription.status == Status.ACTIVE

        # Verificar que se creó una transacción con identificador único
        self.transaction_port.save.assert_called_once()
        saved_transaction = self.transaction_port.save.call_args[0][0]
        assert saved_transaction.user_id == "u001"
        assert saved_transaction.fund_id == "f001"
        assert saved_transaction.amount == 100000
        assert saved_transaction.transaction_type == TransactionType.OPEN
        assert saved_transaction.prev_balance == 500000
        assert saved_transaction.new_balance == 400000
        assert saved_transaction.timestamp is not None

        assert result == expected_subscription

    def test_cancel_subscription_returns_money_to_user(self):
        """
        Regla de negocio: Al cancelar una suscripción,
        el valor de vinculación se retorna al cliente.
        """
        # Arrange
        user = User(
            user_id="u001",
            name="Test User",
            email="test@example.com",
            balance=400000,  # Balance después de suscripción
            notify_channel=NotifyChannel.EMAIL,
            phone="+1-234-567-8900"
        )

        fund = Fund(
            fund_id="f001",
            name="Fondo Básico",
            min_amount=50000,
            category="FPV"
        )

        active_subscription = Subscription(
            user_id="u001",
            fund_id="f001",
            amount=100000,  # Monto a devolver
            status=Status.ACTIVE
        )

        cancelled_subscription = Subscription(
            user_id="u001",
            fund_id="f001",
            amount=100000,
            status=Status.CANCELLED
        )

        self.funds_port.get_by_id.return_value = fund
        self.user_port.get_by_id.return_value = user
        self.user_port.get_by_id.return_value = user
        self.subscription_port.get.return_value = active_subscription
        self.subscription_port.update.return_value = cancelled_subscription

        # Act
        result = self.use_case.cancel_subscription(
            fund_id="f001",
            user_id=user.user_id
        )

        # Assert
        # Verificar que se devolvió el dinero al usuario
        self.user_port.update.assert_called_once_with(
            "u001",
            new_balance=500000  # 400000 + 100000 (monto devuelto)
        )

        # Verificar que se actualizó la suscripción a cancelada
        self.subscription_port.update.assert_called_once_with(
            "u001",
            "f001",
            status=Status.CANCELLED
        )

        # Verificar que se creó transacción de cancelación
        self.transaction_port.save.assert_called_once()
        cancel_transaction = self.transaction_port.save.call_args[0][0]
        assert cancel_transaction.user_id == "u001"
        assert cancel_transaction.fund_id == "f001"
        assert cancel_transaction.amount == 500000  # Balance final
        assert cancel_transaction.transaction_type == TransactionType.OPEN
        assert cancel_transaction.prev_balance == 400000
        assert cancel_transaction.new_balance == 500000

        assert result == cancelled_subscription

    def test_cannot_cancel_inactive_subscription(self):
        """
        Regla de negocio: Solo se pueden cancelar suscripciones activas.
        """
        # Arrange
        user = User(
            user_id="u001",
            name="Test User",
            email="test@example.com",
            balance=400000,
            notify_channel=NotifyChannel.EMAIL,
            phone="+1-234-567-8900"
        )

        fund = Fund(
            fund_id="f001",
            name="Fondo Básico",
            min_amount=50000,
            category="FPV"
        )

        # Suscripción ya cancelada
        inactive_subscription = Subscription(
            user_id="u001",
            fund_id="f001",
            amount=100000,
            status=Status.CANCELLED
        )

        self.funds_port.get_by_id.return_value = fund
        self.user_port.get_by_id.return_value = user
        self.subscription_port.get.return_value = inactive_subscription

        # Act & Assert
        with pytest.raises(ValueError, match="Active subscription not found"):
            self.use_case.cancel_subscription(
                fund_id="f001",
                user_id=user.user_id
            )

        # Verificar que no se realizaron cambios
        self.user_port.update.assert_not_called()
        self.subscription_port.update.assert_not_called()
        self.transaction_port.save.assert_not_called()

    def test_cannot_cancel_nonexistent_subscription(self):
        """
        Regla de negocio: No se puede cancelar una suscripción que no existe.
        """
        # Arrange
        user = User(
            user_id="u001",
            name="Test User",
            email="test@example.com",
            balance=500000,
            notify_channel=NotifyChannel.EMAIL,
            phone="+1-234-567-8900"
        )

        fund = Fund(
            fund_id="f001",
            name="Fondo Básico",
            min_amount=50000,
            category="FPV"
        )

        self.funds_port.get_by_id.return_value = fund
        self.user_port.get_by_id.return_value = user
        self.subscription_port.get.return_value = None

        # Act & Assert
        with pytest.raises(ValueError, match="Active subscription not found"):
            self.use_case.cancel_subscription(
                fund_id="f001",
                user_id=user.user_id
            )

    def test_fund_not_found_raises_error(self):
        """
        Regla de negocio: Validar que el fondo
        existe antes de permitir suscripciones.
        """
        # Arrange
        user = User(
            user_id="u001",
            name="Test User",
            email="test@example.com",
            balance=500000,
            notify_channel=NotifyChannel.EMAIL,
            phone="+1-234-567-8900"
        )

        self.funds_port.get_by_id.return_value = None  # Fondo no existe

        # Act & Assert
        with pytest.raises(ValueError, match="Fund not found"):
            self.use_case.subscribe(
                fund_id="f999",  # ID inexistente
                user_id=user.user_id,
                amount=100000,
                notification_channel="email"
            )
