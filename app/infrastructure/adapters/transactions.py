from app.application.ports.transactions import TransactionPort
from app.domain.models.transaction import Transaction
from typing import Iterable, List, Optional
from datetime import datetime


class TransactionAdapter(TransactionPort):
    def __init__(self, seed: Optional[List[Transaction]] = None):
        self._transactions: List[Transaction] = seed or []

    def get_all(
        self,
        limit: int = 50,
        since: datetime | None = None
    ) -> Iterable[Transaction]:
        """Get all transactions, optionally filtered by a starting date."""
        filtered_transactions = self._transactions
        
        if since:
            # For demo purposes, we'll filter by a simple string comparison
            # In a real implementation, you'd parse the timestamp properly
            filtered_transactions = [
                tx for tx in self._transactions
                if tx.timestamp >= since.isoformat()
            ]
        
        return filtered_transactions[:limit]

    def save(self, transaction: Transaction) -> Transaction:
        """Save a transaction."""
        self._transactions.append(transaction)
        return transaction