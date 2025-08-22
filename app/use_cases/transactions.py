from app.application.ports.transactions import TransactionPort
from datetime import datetime
from typing import Iterable
from app.domain.models.transaction import Transaction


class TransactionUseCase:
    def __init__(self, transaction_port: TransactionPort):
        self.transaction_port = transaction_port

    def get_all_transactions(
            self,
            limit: int = 50,
            since: datetime | None = None
            ) -> Iterable[Transaction]:
        """Get all transactions, optionally filtered by a starting date."""
        if (since is not None):
            return self.transaction_port.get_all(limit=limit, since=since)

        return self.transaction_port.get_all(limit=limit)
    
    def get_transactions_by_user(
            self,
            user_id: str,
            limit: int = 50
            ) -> Iterable[Transaction]:
        """Get all transactions for a specific user."""
        return self.transaction_port.get_by_user(user_id=user_id, limit=limit)
