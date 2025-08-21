from app.application.ports.funds import FundPort
from app.application.ports.subscriptions import SubscriptionPort
from app.domain.models.subscription import Subscription, Status


class SubscriptionUseCase:
    def __init__(
            self, funds_port: FundPort,
            subscription_port: SubscriptionPort,
            ) -> None:
        self._funds_port = funds_port
        self._subscription_port = subscription_port

    def subscribe(
            self,
            fund_id: str,
            user_id: str,
            amount: float
            ) -> Subscription:
        """Subscribe a user to a fund."""
        fund = self._funds_port.get_by_id(fund_id)
        if not fund:
            raise ValueError("Fund not found")

        if amount < fund.min_amount:
            raise ValueError("Amount is less than the minimum required")

        subscription = Subscription(
            user_id=user_id,
            fund_id=fund_id,
            amount=amount,
            status=Status.ACTIVE,
        )
        subscription = self._subscription_port.save(subscription)
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
