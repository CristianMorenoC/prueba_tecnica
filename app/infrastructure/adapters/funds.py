from app.domain.models.fund import Fund
from typing import List, Optional, Tuple
from app.application.ports.funds import FundPort


class FundAdapter(FundPort):

    def __init__(self, seed: Optional[List[Fund]] = None):
        self._funds: List[Fund] = seed or [
            Fund(
                fund_id="1",
                name="FPV BTG Pactual Recaudadora",
                min_amount=75000,
                category="FPV"
                ),
            Fund(
                fund_id="2",
                name="FPV Renta Fija Conservadora",
                min_amount=50000,
                category="FPV"
                ),
            Fund(
                fund_id="3",
                name="ETF S&P 500 USD",
                min_amount=100000,
                category="ETF"
                ),
            Fund(
                fund_id="4",
                name="ETF Nasdaq 100 USD",
                min_amount=100000,
                category="ETF"
                ),
            Fund(
                fund_id="5",
                name="FPV Liquidez Diaria",
                min_amount=20000,
                category="FPV"
                ),
        ]
        self._funds.sort(key=lambda x: x.fund_id)

    def get_by_id(self, fund_id: str) -> Fund:
        """Get a fund by its ID."""
        for fund in self._funds:
            if fund.fund_id == fund_id:
                return fund
        raise ValueError("Fund not found")

    def list_all(
            self,
            limit=50,
            last_key: Optional[str] = None
            ) -> Tuple[List[Fund], Optional[str]]:
        """Get all funds by pagination."""
        start_idx = 0
        if last_key:
            for idx, fund in enumerate(self._funds):
                if fund.fund_id == last_key:
                    start_idx = idx + 1
                    break
        page = self._funds[start_idx:start_idx + limit]
        next_page = (
            page[-1].fund_id
            if (start_idx + limit) < len(self._funds) and page
            else None
        )
        return (page, next_page)
