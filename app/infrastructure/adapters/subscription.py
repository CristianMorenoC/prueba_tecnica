import boto3
import os
from datetime import datetime
from botocore.exceptions import ClientError
from app.application.ports.subscriptions import SubscriptionPort
from app.domain.models.subscription import Subscription, Status


class SubscriptionAdapter(SubscriptionPort):
    def __init__(self, dynamodb_resource=None):
        if dynamodb_resource is None:
            self.dynamodb = boto3.resource(
                'dynamodb',
                aws_access_key_id=os.getenv('AWS_ACCESS_KEY_ID'),
                aws_secret_access_key=os.getenv('AWS_SECRET_ACCESS_KEY'),
                region_name=os.getenv('AWS_DEFAULT_REGION', 'us-east-1')
            )
        else:
            self.dynamodb = dynamodb_resource

        self.subscriptions_table = self.dynamodb.Table('Subscriptions')

    def subscribe(
        self,
        user_id: str,
        fund_id: str,
        amount: float
    ) -> Subscription:
        """Subscribe a user to a fund."""
        try:
            subscription = Subscription(
                user_id=user_id,
                fund_id=fund_id,
                amount=amount,
                status=Status.ACTIVE,
                created_at=datetime.now().isoformat()
            )

            return self.save(subscription)

        except ClientError as e:
            raise Exception(
                "Error creating subscription: "
                f"{e.response['Error']['Message']}"
            )

    def unsubscribe(self, user_id: str, fund_id: str) -> Subscription:
        """Unsubscribe a user from a fund (change status to cancelled)."""
        try:
            response = self.subscriptions_table.update_item(
                Key={'user_id': user_id, 'fund_id': fund_id},
                UpdateExpression=(
                    'SET #status = :cancelled, cancelled_at = :timestamp'
                ),
                ExpressionAttributeNames={'#status': 'status'},
                ExpressionAttributeValues={
                    ':cancelled': Status.CANCELLED.value,
                    ':timestamp': datetime.now().isoformat()
                },
                ReturnValues='ALL_NEW'
            )

            item = response['Attributes']
            return Subscription(
                user_id=item['user_id'],
                fund_id=item['fund_id'],
                amount=float(item['amount']),
                status=Status(item['status']),
                created_at=item.get('created_at'),
                cancelled_at=item.get('cancelled_at')
            )

        except ClientError as e:
            if e.response['Error']['Code'] == 'ResourceNotFoundException':
                raise ValueError("Subscription not found")
            raise Exception(
                f"Error cancelling subscription: "
                f"{e.response['Error']['Message']}"
            )
