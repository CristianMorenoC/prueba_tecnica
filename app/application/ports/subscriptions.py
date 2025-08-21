from typing import Protocol, Optional, Iterable
from app.domain.models.subscription import Subscription


class SubscriptionPort(Protocol):

    def _add(self, subscription: Subscription) -> Subscription:
        """Add a subscription from seed for testing."""

    def get(self, user_id: str, fund_id: str) -> Optional[Subscription]:
        """Get a subscription by user ID and fund ID."""

    def list_by_user(
            self,
            user_id: str,
            status: str | None = None
            ) -> Iterable[Subscription]:
        """List subscriptions by user ID, filtered by status."""

    def save(self, subscription: Subscription) -> Subscription:
        """Save a subscription."""

    def cancel(self, user_id: str, fund_id: str) -> Subscription:
        """Cancel a subscription."""
