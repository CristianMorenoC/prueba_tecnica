from fastapi import Depends
from app.run import app
from app.use_cases.subscriptions import SubscriptionUseCase
from app.use_cases.transactions import TransactionUseCase
from app.domain.models.user import User, NotifyChannel
from app.domain.models.requests import SubscribeRequest
from app.infrastructure.dependencies import (
    get_subscription_use_case,
    get_transaction_use_case
)


@app.get("/user/{user_id}/transactions")
async def get_transactions_by_user(
    user_id: str,
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


@app.delete("/user/{user_id}/subscribe/{fund_id}")
async def cancel_subscribtion(
    fund_id: str,
    user_id: str,
    use_case: SubscriptionUseCase = Depends(get_subscription_use_case)
):
    """Subscribe a user to a fund."""
    return use_case.cancel_subscription(
        fund_id=fund_id,
        user=User(
            user_id=user_id,
            balance=300000,
            email="eve@example.com",
            name="Eve",
            notify_channel=NotifyChannel.EMAIL,
            phone="+1-202-555-0105"
        ),
    )


@app.get("/transactions")
async def history(
    use_case: TransactionUseCase = Depends(get_transaction_use_case)
):
    """Get transaction history."""
    return use_case.get_all_transactions()
