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
        if (since is None):
            since = datetime.now()
        elif (since > datetime.now()):
            raise ValueError("Since date cannot be in the future")
        return self.transaction_port.get_all(limit=limit, since=since)
