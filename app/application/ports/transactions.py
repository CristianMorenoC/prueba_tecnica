from typing import Protocol, Iterable
from datetime import datetime
from app.domain.models.transaction import Transaction


class TransactionPort(Protocol):
    def get_all(
            self,
            limit: int = 50,
            since: datetime | None = None
            ) -> Iterable[Transaction]:
        """transactions by user ID, filtered by a starting date."""
