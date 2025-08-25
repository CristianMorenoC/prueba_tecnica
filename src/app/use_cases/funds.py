from application.ports.funds import FundPort


class FundUseCase:
    """Use case for retrieving all available funds."""

    def __init__(self, fund_repository: FundPort):
        self.fund_repository = fund_repository

    def list_all_funds(self):
        """Retrieve all funds from the repository."""
        try:
            print("[FUNDS DEBUG] Starting list_all_funds")
            result = self.fund_repository.list_all()
            print(f"[FUNDS DEBUG] Repository returned: {result}")
            return result
        except Exception as e:
            print(f"[FUNDS DEBUG] Error in list_all_funds: {str(e)}")
            raise
