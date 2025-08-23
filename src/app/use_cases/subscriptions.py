from application.ports.funds import FundPort
from application.ports.subscriptions import SubscriptionPort
from application.ports.transactions import TransactionPort
from domain.models.subscription import Subscription, Status
from application.ports.users import UserPort
from domain.models.user import User
from domain.models.transaction import Transaction, TransactionType
from datetime import datetime


class SubscriptionUseCase:
    def __init__(
            self, funds_port: FundPort,
            subscription_port: SubscriptionPort,
            transaction_port: TransactionPort,
            user_port: UserPort
            ) -> None:
        self._funds_port = funds_port
        self._subscription_port = subscription_port
        self._user_port = user_port
        self._transaction_port = transaction_port

    def subscribe(
            self,
            fund_id: str,
            user_id: str,
            amount: int,
            notification_channel: str
            ) -> Subscription:
        """Subscribe a user to a fund."""
        fund = self._funds_port.get_by_id(fund_id)
        if not fund:
            raise ValueError("Fund not found")

        # check if the amount is less than the minimum required
        if amount < fund.min_amount:
            raise ValueError(f"No tiene saldo disponible para vincularse al fondo ${fund.name}")

        # get user
        user = self._user_port.get_by_id(user_id)
        if not user:
            raise ValueError("User not found")
        # calculate new balance
        new_balance = user.balance - amount

        # check if the user has enough balance
        if new_balance < 0:
            raise ValueError(f"No hay suficiente saldo para vincularse al fondo ${fund.name}")
        
        # update user balance
        self._user_port.update(user.user_id, new_balance=new_balance)

        # create subscription
        subscription = Subscription(
            user_id=user.user_id,
            fund_id=fund_id,
            amount=amount,
            status=Status.ACTIVE,
            notificationChannel=notification_channel
        )
        subscription = self._subscription_port.save(subscription)

        # create a transaction for the subscription
        transaction = Transaction(
            user_id=user.user_id,
            fund_id=fund_id,
            amount=amount,
            transaction_type=TransactionType.OPEN,
            timestamp=datetime.now().isoformat(),
            prev_balance=user.balance,
            new_balance=new_balance
        )

        self._transaction_port.save(transaction)
        return subscription

    def cancel_subscription(
            self,
            fund_id: str,
            user_id: str,
            ) -> Subscription:
        """Subscribe a user to a fund."""
        fund = self._funds_port.get_by_id(fund_id)
        if not fund:
            raise ValueError("Fund not found")

        # get user
        user = self._user_port.get_by_id(user_id)

        if not user:
            raise ValueError("User not found")

        # get active user's active subscription
        subs = self._subscription_port.get(user.user_id, fund_id)

        if not subs or subs.status != Status.ACTIVE:
            raise ValueError("Active subscription not found")

        # calculate new balance
        new_balance = user.balance + subs.amount

        # update user balance
        self._user_port.update(user.user_id, new_balance=new_balance)

        subscription = self._subscription_port.update(
            user.user_id,
            fund_id, status=Status.CANCELLED
        )

        # create a transaction for the subscription
        transaction = Transaction(
            user_id=user.user_id,
            fund_id=fund_id,
            amount=new_balance,
            transaction_type=TransactionType.OPEN,
            timestamp=datetime.now().isoformat(),
            prev_balance=user.balance,
            new_balance=new_balance
        )

        self._transaction_port.save(transaction)
        return subscription
