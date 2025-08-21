from app.application.ports.subscriptions import SubscriptionPort
from typing import Optional, Dict, Tuple, Iterable
from app.domain.models.subscription import Subscription, Status


Key = Tuple[str, str]  # (user_id, fund_id)


class SubscriptionAdapter(SubscriptionPort):
    def __init__(self, seed: Optional[list[Subscription]] = None) -> None:
        self._subscriptions: Dict[Key, Subscription] = {}
        if seed:
            for subscription in seed:
                self._add(subscription)

    def _add(self, subscription: Subscription) -> None:
        """Add a subscription to the repository."""
        key = (subscription.user_id, subscription.fund_id)
        self._subscriptions[key] = subscription

    def get(self, user_id: str, fund_id: str) -> Optional[Subscription]:
        """Get a subscription by user ID and fund ID."""
        key = (user_id, fund_id)
        for subscription_key, subscription in self._subscriptions.items():
            if subscription_key == key:
                return subscription
        return None

    def list_by_user(
            self,
            user_id: str,
            status: Optional[str] = "active"
            ) -> Iterable[Subscription]:
        """List subscriptions by user ID, filtered by status."""
        for subscription in self._subscriptions.values():
            if (
                subscription.user_id == user_id
                and (status is None or subscription.status == status)
            ):
                yield subscription

    def save(self, subscription: Subscription) -> Subscription:
        """Save a subscription."""
        key = (subscription.user_id, subscription.fund_id)
        self._subscriptions[key] = subscription
        return subscription

    def cancel(self, user_id: str, fund_id: str) -> Subscription:
        """Cancel a subscription."""
        key = (user_id, fund_id)
        subscription = self._subscriptions.get(key)
        if not subscription:
            raise ValueError("Subscription not found")
        if subscription.status == "CANCELLED":
            raise ValueError("Subscription already cancelled")
        subscription.status = Status.CANCELLED
        self._subscriptions[key] = subscription
        return subscription
