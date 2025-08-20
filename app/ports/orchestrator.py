from typing import Protocol
from datetime import datetime


class SubscriptionOrchestrator(Protocol):
    def open(self, *,
             user_id: str,
             fund_id: str,
             amount: int,
             tx_id: str,
             ts: datetime,
             expected_min_balance: int | None = None) -> None:
        """Open a new subscription."""
    def cancel(self, *,
               user_id: str,
               fund_id: str,
               amount: int,
               tx_id: str,
               ts: datetime) -> None:
        """Cancel an existing subscription."""
