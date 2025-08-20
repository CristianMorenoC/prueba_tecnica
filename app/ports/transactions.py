from typing import Protocol, Iterable
from datetime import datetime
from app.domain.models.transaction import Transaction


class TransactionRepo(Protocol):
    def list_by_user(
            self,
            user_id: str,
            limit: int = 50,
            since: datetime | None = None
            ) -> Iterable[Transaction]:
        """transactions by user ID, filtered by a starting date."""
