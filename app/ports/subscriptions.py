from typing import Protocol, Optional, Iterable
from app.domain.models.subscription import Subscription


class SubscriptionRepo(Protocol):
    def get(self, user_id: str, fund_id: str) -> Optional[Subscription]:
        """Get a subscription by user ID and fund ID."""
    def list_by_user(
            self,
            user_id: str,
            status: str | None = None
            ) -> Iterable[Subscription]:
        """List subscriptions by user ID, filtered by status."""
