from fastapi import Depends
from app.main import app
from app.use_cases.subscriptions import SubscriptionUseCase
from app.use_cases.transactions import TransactionUseCase
from app.domain.models.requests import SubscribeRequest
from app.domain.models.user import User, NotifyChannel
from app.infrastructure.dependencies import (
    get_subscription_use_case,
    get_transaction_use_case
)


@app.get("/user/transactions")
async def get_transactions_by_user(
    user_id: str = "u002",  # TODO: Get from authentication
    use_case: TransactionUseCase = Depends(get_transaction_use_case)
):
    """Get all transactions for a user."""
    return use_case.get_transactions_by_user(
        user_id=user_id
    )


@app.post("/user/{user_id}/subscribe/{fund_id}")
async def subscribe(
    fund_id: str,
    request: SubscribeRequest,
    use_case: SubscriptionUseCase = Depends(get_subscription_use_case)
):
    """Subscribe a user to a fund."""
    return use_case.subscribe(
        user=User(
            user_id="u005",
            balance=300000,
            email="eve@example.com",
            name="Eve",
            notify_channel=NotifyChannel.EMAIL,
            phone="+1-202-555-0105"
        ),
        fund_id=fund_id,
        amount=request.amount
    )


@app.delete("/user/{fund_id}/subscribe")
async def unsubscribedos(
    fund_id: str,
    user_id: str = "u006",  # TODO: Get from authentication
    use_case: SubscriptionUseCase = Depends(get_subscription_use_case)
):
    """Cancel a user's subscription to a fund."""
    return use_case.cancel_subscription(
        fund_id=fund_id,
        user_id=user_id
    )


@app.get("/transactions")
async def history(
    use_case: TransactionUseCase = Depends(get_transaction_use_case)
):
    """Get transaction history."""
    return use_case.get_all_transactions()
