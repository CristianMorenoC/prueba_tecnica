from typing import Protocol, Iterable
from datetime import datetime
from domain.models.transaction import Transaction


class TransactionPort(Protocol):
    def get_all(
            self,
            limit: int = 50,
            since: datetime | None = None
            ) -> Iterable[Transaction]:
        """Get all transactions, optionally filtered by a starting date."""

    def get_by_fund(
            self,
            fund_id: str,
            limit: int = 50
            ) -> Iterable[Transaction]:
        """Get all transactions for a specific fund."""

    def get_by_user(
            self,
            user_id: str,
            limit: int = 50
            ) -> Iterable[Transaction]:
        """Get all transactions for a specific user."""

    def save(self, transaction: Transaction) -> Transaction:
        """Save a transaction."""
