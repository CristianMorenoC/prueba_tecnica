from fastapi import Depends
from main import app
from use_cases.subscriptions import SubscriptionUseCase
from use_cases.transactions import TransactionUseCase
from use_cases.user import UserUseCase
from use_cases.funds import FundUseCase
from domain.models.requests import SubscribeRequest
from domain.models.user import UserCreateRequest
from infrastructure.dependencies import (
    get_subscription_use_case,
    get_transaction_use_case,
    get_user_use_case,
    get_fund_use_case
)


@app.get("/user/{user_id}/transactions")
async def get_transactions_by_user(
    user_id: str,
    use_case: TransactionUseCase = Depends(get_transaction_use_case)
):
    """Get all transactions for a user."""
    result = use_case.get_transactions_by_user(user_id=user_id)
    # Convert generator to list for JSON serialization
    return list(result)


@app.post("/user/{user_id}/subscribe/{fund_id}")
async def subscribe(
    fund_id: str,
    user_id: str,
    request: SubscribeRequest,
    use_case: SubscriptionUseCase = Depends(get_subscription_use_case)
):
    """Subscribe a user to a fund."""
    return use_case.subscribe(
        user_id=user_id,
        fund_id=fund_id,
        amount=request.amount,
        notification_channel=request.notification_channel
    )

@app.post("/user/create")
async def create_user(
    request: UserCreateRequest,
    use_case: UserUseCase = Depends(get_user_use_case)
):
    """Create a new user."""
    return use_case.create_user(request)


@app.delete("/user/{user_id}/subscribe/{fund_id}")
async def cancel_subs(
    fund_id: str,
    user_id: str,  # TODO: Get from authentication
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
    try:
        print("[TRANSACTIONS DEBUG] Starting transactions endpoint")
        result = use_case.get_all_transactions()
        # Convert generator to list for JSON serialization
        transactions = list(result)
        print(f"[TRANSACTIONS DEBUG] Use case returned {len(transactions)} transactions")
        return transactions
    except Exception as e:
        print(f"[TRANSACTIONS DEBUG] Error in transactions endpoint: {str(e)}")
        raise


@app.get("/funds/")
async def get_all_funds(
    usecase: FundUseCase = Depends(get_fund_use_case)
):
    """Get all available funds."""
    try:
        print("[FUNDS ROUTE DEBUG] Starting funds endpoint")
        result = usecase.list_all_funds()
        print(f"[FUNDS ROUTE DEBUG] Use case returned: {result}")
        return result
    except Exception as e:
        print(f"[FUNDS ROUTE DEBUG] Error in funds endpoint: {str(e)}")
        raise
