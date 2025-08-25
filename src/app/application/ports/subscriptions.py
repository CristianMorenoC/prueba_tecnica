from typing import Protocol, Optional, Iterable, Any
from domain.models.subscription import Subscription


class SubscriptionPort(Protocol):

    def _add(self, subscription: Subscription) -> Subscription:
        """Add a subscription from seed for testing."""

    def get(self, user_id: str, fund_id: str) -> Optional[Subscription]:
        """Get a subscription by user ID and fund ID."""

    def update(self, user_id: str, fund_id: str, **params: Any) -> Subscription:
        """Update a subscription."""

    def list_by_user(
            self,
            user_id: str,
            status: str | None = None
            ) -> Iterable[Subscription]:
        """List subscriptions by user ID, filtered by status."""

    def save(self, subscription: Subscription, user_email: str = None, user_phone: str = None) -> Subscription:
        """Save a subscription."""

    def cancel(self, user_id: str, fund_id: str) -> Subscription:
        """Cancel a subscription."""

    def subscribe(
        self,
        user_id: str,
        fund_id: str,
        amount: int
    ) -> Subscription:
        """Subscribe a user to a fund."""

    def unsubscribe(self, user_id: str, fund_id: str) -> Subscription:
        """Unsubscribe a user from a fund (change status to cancelled)."""
