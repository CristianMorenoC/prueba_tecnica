from app.application.ports.funds import FundPort
from app.application.ports.subscriptions import SubscriptionPort
from app.application.ports.transactions import TransactionPort
from app.domain.models.subscription import Subscription, Status
from app.application.ports.users import UserPort
from app.domain.models.user import User
from app.domain.models.transaction import Transaction, TransactionType
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
            user: User,
            amount: int
            ) -> Subscription:
        """Subscribe a user to a fund."""
        fund = self._funds_port.get_by_id(fund_id)
        if not fund:
            raise ValueError("Fund not found")
        
        # check if the amount is less than the minimum required
        if amount < fund.min_amount:
            raise ValueError("Amount is less than the minimum required")
        
        # calculate new balance
        new_balance = user.balance - amount

        # check if the user has enough balance
        if new_balance < 0:
            raise ValueError("Insufficient balance")
        
        # update user balance
        self._user_port.update(user.user_id, new_balance=new_balance)

        # create subscription
        subscription = Subscription(
            user_id=user.user_id,
            fund_id=fund_id,
            amount=amount,
            status=Status.ACTIVE,
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
            user_id: str,
            fund_id: str
            ) -> Subscription:
        """Cancel a user's subscription to a fund."""
        subscription = self._subscription_port.cancel(user_id, fund_id)
        if (not subscription):
            raise ValueError("Subscription not found")
        return subscription
