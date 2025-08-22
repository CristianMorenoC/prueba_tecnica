from domain.models.fund import Fund
from typing import Protocol, Tuple


class FundPort(Protocol):
    def get_by_id(self, fund_id: str) -> Fund:
        """Get a fund by its ID."""

    def list_all(
                self,
                limit: int = 50,
                last_key: str | None = None
                ) -> Tuple[list[Fund], str | None]:
        """List all funds."""
