import boto3
from datetime import datetime
import random
from botocore.exceptions import ClientError
from boto3.dynamodb.conditions import Attr, Key
from application.ports.transactions import TransactionPort
from domain.models.transaction import Transaction, TransactionType
from typing import Iterable, Dict, Any
from config import APPCHALLENGE_TABLE_NAME, AWS_REGION


def _generate_random_timestamp():
    """Generate a random timestamp for missing transaction dates."""
    # Generate random date between 2024-01-01 and 2025-12-31
    start_year, end_year = 2024, 2025
    year = random.randint(start_year, end_year)
    month = random.randint(1, 12)
    day = random.randint(1, 28)  # Safe for all months
    hour = random.randint(0, 23)
    minute = random.randint(0, 59)
    second = random.randint(0, 59)
    
    return f"{year}-{month:02d}-{day:02d}T{hour:02d}:{minute:02d}:{second:02d}Z"


class TransactionAdapter(TransactionPort):
    def __init__(self, dynamodb_resource=None):
        if dynamodb_resource is None:
            self.dynamodb = boto3.resource(
                'dynamodb',
                region_name=AWS_REGION
            )
        else:
            self.dynamodb = dynamodb_resource

        self.transactions_table = self.dynamodb.Table(APPCHALLENGE_TABLE_NAME)

    def get_all(
        self,
        limit: int = 50,
        since: datetime | None = None
    ) -> Iterable[Transaction]:
        """Get all transactions, optionally filtered by a starting date."""
        try:
            scan_kwargs: Dict[str, Any] = {
                'Limit': limit,
                'FilterExpression': Attr('SK').begins_with('TX#')
            }

            if since:
                scan_kwargs['FilterExpression'] = (
                    scan_kwargs['FilterExpression'] &
                    Attr('timestamp').gte(since.isoformat())
                )

            response = self.transactions_table.scan(**scan_kwargs)

            for item in response.get('Items', []):
                yield Transaction(
                    user_id=item.get('user_id'),
                    fund_id=item.get('fund_id'),
                    amount=int(item.get('amount', 0)),
                    transaction_type=TransactionType(
                        item.get('type', 'open').lower()
                    ),
                    timestamp=item.get('ts') or _generate_random_timestamp(),
                    prev_balance=int(item.get('prev_balance', 0)),
                    new_balance=int(item.get('new_balance', 0))
                )

        except ClientError as e:
            raise Exception(
                "Error retrieving all transactions: "
                f"{e.response['Error']['Message']}"
            )

    def get_by_fund(
        self,
        fund_id: str,
        limit: int = 50
    ) -> Iterable[Transaction]:
        """Get all transactions for a specific fund."""
        try:
            response = self.transactions_table.query(
                IndexName='fund_id-index',
                KeyConditionExpression=Key('fund_id').eq(fund_id),
                FilterExpression=Attr('SK').begins_with('TX#'),
                Limit=limit
            )

            for item in response.get('Items', []):
                yield Transaction(
                    user_id=item.get('user_id'),
                    fund_id=item.get('fund_id'),
                    amount=int(item.get('amount', 0)),
                    transaction_type=TransactionType(
                        item.get('type', 'open').lower()
                    ),
                    timestamp=item.get('ts') or _generate_random_timestamp(),
                    prev_balance=int(item.get('prev_balance', 0)),
                    new_balance=int(item.get('new_balance', 0))
                )

        except ClientError as e:
            raise Exception(
                f"Error retrieving transactions by fund: "
                f"{e.response['Error']['Message']}"
            )

    def get_by_user(
        self,
        user_id: str,
        limit: int = 50
    ) -> Iterable[Transaction]:
        """Get all transactions for a specific user."""
        try:
            response = self.transactions_table.query(
                KeyConditionExpression=(
                    Key('PK').eq(f'USER#{user_id}') &
                    Key('SK').begins_with('TX#')
                ),
                Limit=limit
            )

            for item in response.get('Items', []):
                yield Transaction(
                    user_id=item.get('user_id'),
                    fund_id=item.get('fund_id'),
                    amount=int(item.get('amount', 0)),
                    transaction_type=TransactionType(
                        item.get('type', 'open').lower()
                    ),
                    timestamp=item.get('ts') or _generate_random_timestamp(),
                    prev_balance=int(item.get('prev_balance', 0)),
                    new_balance=int(item.get('new_balance', 0))
                )

        except ClientError as e:
            raise Exception(
                "Error retrieving transactions by user: "
                f"{e.response['Error']['Message']}"
            )

    def save(self, transaction: Transaction) -> Transaction:
        """Save a transaction."""
        try:
            # Generate unique transaction ID
            timestamp_clean = transaction.timestamp.replace(':', '').replace('-', '').replace('.', '')[:15]
            transaction_id = f"T{timestamp_clean}"
            
            self.transactions_table.put_item(
                Item={
                    'PK': f'USER#{transaction.user_id}',
                    'SK': f'TX#{timestamp_clean}#{transaction_id}',
                    'user_id': transaction.user_id,
                    'fund_id': transaction.fund_id,
                    'amount': transaction.amount,
                    'transaction_type': transaction.transaction_type.value,
                    'timestamp': transaction.timestamp,
                    'prev_balance': transaction.prev_balance,
                    'new_balance': transaction.new_balance
                }
            )
            return transaction

        except ClientError as e:
            raise Exception(
                f"Error saving transaction: {e.response['Error']['Message']}"
            )
