from fastapi import Depends
from app.main import app
from app.use_cases.subscriptions import SubscriptionUseCase
from app.use_cases.transactions import TransactionUseCase
from app.infrastructure.dependencies import (
    get_subscription_use_case,
    get_transaction_use_case
)


@app.post("/subscribe/{fund_id}")
async def subscribe(
    fund_id: str,
    user_id: str = "user123",  # TODO: Get from authentication
    amount: float = 100.0,     # TODO: Get from request body
    use_case: SubscriptionUseCase = Depends(get_subscription_use_case)
):
    """Subscribe a user to a fund."""
    return use_case.subscribe(
        fund_id=fund_id,
        user_id=user_id,
        amount=amount
    )


@app.post("/unsubscribe/{fund_id}")
async def unsubscribe(
    fund_id: str,
    user_id: str = "user123",  # TODO: Get from authentication
    use_case: SubscriptionUseCase = Depends(get_subscription_use_case)
):
    """Cancel a user's subscription to a fund."""
    return use_case.cancel_subscription(
        fund_id=fund_id,
        user_id=user_id
    )


@app.get("/history")
async def history(
    use_case: TransactionUseCase = Depends(get_transaction_use_case)
):
    """Get transaction history."""
    return use_case.get_all_transactions()
