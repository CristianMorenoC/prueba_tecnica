from fastapi import Depends
from ..run import app
from ..use_cases.subscriptions import SubscriptionUseCase
from ..use_cases.transactions import TransactionUseCase
from ..domain.models.requests import SubscribeRequest
from ..infrastructure.dependencies import (
    get_subscription_use_case,
    get_transaction_use_case
)


@app.get("/user/{user_id}/transactions")
async def get_all_by_user(
    user_id: str,
    use_case: TransactionUseCase = Depends(get_transaction_use_case)
):
    """Get all transactions for a user."""
    return use_case.get_transactions_by_user(
        user_id=user_id
    )


@app.post("/user/{user_id}/subscribe/{fund_id}")
async def suscribe_user(
    user_id: str,
    fund_id: str,
    request: SubscribeRequest,
    use_case: SubscriptionUseCase = Depends(get_subscription_use_case)
):
    """Subscribe a user to a fund."""
    return use_case.subscribe(
        user_id=user_id,
        fund_id=fund_id,
        amount=request.amount,
        notification_channel=request.notification_channel,
    )


@app.delete("/user/{user_id}/subscribe/{fund_id}")
async def cancel_subscribtion(
    fund_id: str,
    user_id: str,
    use_case: SubscriptionUseCase = Depends(get_subscription_use_case)
):
    """Subscribe a user to a fund."""
    return use_case.cancel_subscription(
        fund_id=fund_id,
        user_id=user_id,
    )


@app.get("/transactions")
async def history(
    use_case: TransactionUseCase = Depends(get_transaction_use_case)
):
    """Get transaction history."""
    return use_case.get_all_transactions()
