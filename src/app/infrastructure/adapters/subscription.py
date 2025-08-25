import boto3
from datetime import datetime
from botocore.exceptions import ClientError
from boto3.dynamodb.conditions import Attr
from application.ports.subscriptions import SubscriptionPort
from domain.models.subscription import Subscription, Status
from typing import Optional, Iterable, Any
from config import APPCHALLENGE_TABLE_NAME, AWS_REGION


class SubscriptionAdapter(SubscriptionPort):
    def __init__(self, dynamodb_resource=None):
        if dynamodb_resource is None:
            self.dynamodb = boto3.resource(
                'dynamodb',
                region_name=AWS_REGION
            )
        else:
            self.dynamodb = dynamodb_resource

        self.subscriptions_table = self.dynamodb.Table(APPCHALLENGE_TABLE_NAME)

    def subscribe(
        self,
        user_id: str,
        fund_id: str,
        amount: int,
        notification_channel: str,
        user_email: str = None,
        user_phone: str = None
    ) -> Subscription:
        """Subscribe a user to a fund."""
        try:
            subscription = Subscription(
                user_id=user_id,
                fund_id=fund_id,
                amount=amount,
                status=Status.ACTIVE,
                created_at=datetime.now().isoformat(),
                notificationChannel=notification_channel
            )

            return self.save(subscription, user_email=user_email, user_phone=user_phone)

        except ClientError as e:
            raise Exception(
                "Error creating subscription: "
                f"{e.response['Error']['Message']}"
            )

    def unsubscribe(self, user_id: str, fund_id: str) -> Subscription:
        """Unsubscribe a user from a fund (change status to cancelled)."""
        try:
            response = self.subscriptions_table.update_item(
                Key={
                    'PK': f'USER#{user_id}',
                    'SK': f'SUB#{fund_id}'
                },
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
                amount=int(item['amount']),
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

    def _add(self, subscription: Subscription) -> Subscription:
        """Add a subscription from seed for testing."""
        return self.save(subscription)

    def get(self, user_id: str, fund_id: str) -> Optional[Subscription]:
        """Get a subscription by user ID and fund ID."""
        try:
            response = self.subscriptions_table.get_item(
                Key={
                    'PK': f'USER#{user_id}',
                    'SK': f'SUB#{fund_id}'
                }
            )

            if 'Item' not in response:
                return None

            item = response['Item']
            return Subscription(
                user_id=item.get('user_id'),
                fund_id=item.get('fund_id'),
                amount=int(item.get('amount', 0)),
                status=Status(item.get('status')),
                created_at=item.get('created_at'),
                cancelled_at=item.get('cancelled_at')
            )

        except ClientError as e:
            raise Exception(
                f"Error retrieving subscription: {
                    e.response['Error']['Message']
                }"
            )

    def update(
            self,
            user_id: str,
            fund_id: str,
            **params: Any
            ) -> Subscription:
        """Update a subscription."""
        try:
            if not params:
                raise ValueError("No fields to update")

            # Build update expression dynamically
            update_expression = "SET "
            expression_values = {}
            expression_names = {}

            for key, value in params.items():
                attr_name = f"#{key}"
                attr_value = f":{key}"
                update_expression += f"{attr_name} = {attr_value}, "
                expression_names[attr_name] = key
                expression_values[attr_value] = (
                    value.value if hasattr(value, 'value') else value
                    )

            # Remove trailing comma
            update_expression = update_expression.rstrip(", ")

            response = self.subscriptions_table.update_item(
                Key={
                    'PK': f'USER#{user_id}',
                    'SK': f'SUB#{fund_id}'
                },
                UpdateExpression=update_expression,
                ExpressionAttributeNames=expression_names,
                ExpressionAttributeValues=expression_values,
                ReturnValues='ALL_NEW'
            )

            item = response['Attributes']
            return Subscription(
                user_id=item.get('user_id'),
                fund_id=item.get('fund_id'),
                amount=int(item.get('amount', 0)),
                status=Status(item.get('status')),
                created_at=item.get('created_at'),
                cancelled_at=item.get('cancelled_at')
            )

        except ClientError as e:
            raise Exception(
                f"Error updating subscription: {
                    e.response['Error']['Message']
                }"
            )

    def list_by_user(
        self,
        user_id: str,
        status: str | None = None
    ) -> Iterable[Subscription]:
        """List subscriptions by user ID, filtered by status."""
        try:
            scan_kwargs = {
                'FilterExpression': Attr('PK').eq(f'USER#{user_id}') & Attr('SK').begins_with('SUB#')
            }

            if status:
                scan_kwargs['FilterExpression'] = (
                    scan_kwargs['FilterExpression'] & Attr('status').eq(status)
                )

            response = self.subscriptions_table.scan(**scan_kwargs)

            for item in response.get('Items', []):
                yield Subscription(
                    user_id=item.get('user_id'),
                    fund_id=item.get('fund_id'),
                    amount=int(item.get('amount', 0)),
                    status=Status(item.get('status')),
                    created_at=item.get('created_at'),
                    cancelled_at=item.get('cancelled_at')
                )

        except ClientError as e:
            raise Exception(
                f"Error listing subscriptions by user: {e.response['Error']['Message']}"
            )

    def save(self, subscription: Subscription, user_email: str = None, user_phone: str = None) -> Subscription:
        """Save a subscription."""
        try:
            item = {
                'PK': f'USER#{subscription.user_id}',
                'SK': f'SUB#{subscription.fund_id}',
                'user_id': subscription.user_id,
                'fund_id': subscription.fund_id,
                'amount': subscription.amount,
                'status': subscription.status.value,
                'created_at': subscription.created_at,
                'notificationChannel': subscription.notificationChannel
            }

            # Add user contact information for notifications
            if user_email:
                item['email'] = user_email
                print(f"[SUBSCRIPTION DEBUG] Adding email: {user_email}")
            if user_phone:
                item['phone'] = user_phone  
                print(f"[SUBSCRIPTION DEBUG] Adding phone: {user_phone}")
            
            print(f"[SUBSCRIPTION DEBUG] Final item being saved: {item}")

            if subscription.cancelled_at:
                item['cancelled_at'] = subscription.cancelled_at

            self.subscriptions_table.put_item(Item=item)
            return subscription

        except ClientError as e:
            raise Exception(
                f"Error saving subscription: {e.response['Error']['Message']}"
            )

    def cancel(self, user_id: str, fund_id: str) -> Subscription:
        """Cancel a subscription."""
        return self.unsubscribe(user_id, fund_id)
