import boto3
from botocore.exceptions import ClientError
from application.ports.users import UserPort
from domain.models.user import User, NotifyChannel
from typing import Any
from config import APPCHALLENGE_TABLE_NAME, AWS_REGION


class UserAdapter(UserPort):
    def __init__(self, dynamodb_resource=None):
        if dynamodb_resource is None:
            self.dynamodb = boto3.resource(
                'dynamodb',
                region_name=AWS_REGION
            )
        else:
            self.dynamodb = dynamodb_resource

        self.users_table = self.dynamodb.Table(APPCHALLENGE_TABLE_NAME)

    def get_by_id(self, user_id: str) -> User:
        """Get a user by their ID."""
        try:
            response = self.users_table.get_item(
                Key={
                    'PK': f'USER#{user_id}',
                    'SK': 'PROFILE'
                }
            )

            if 'Item' not in response:
                raise ValueError(f"User with ID {user_id} not found")

            item = response['Item']
            return User(
                user_id=item.get('user_id'),
                name=item.get('name'),
                email=item.get('email'),
                phone=item.get('phone'),
                balance=int(item.get('balance', 0)),
                notify_channel=NotifyChannel(item.get('notify_channel'))
            )

        except ClientError as e:
            raise Exception(
                f"Error retrieving user: {e.response['Error']['Message']}"
            )

    def update(self, user_id: str, **params: Any) -> User:
        """Update a user."""
        try:
            # Build update expression dynamically
            update_expression = "SET "
            expression_values = {}
            expression_names = {}

            for key, value in params.items():
                if key != 'user_id':
                    attr_name = f"#{key}"
                    attr_value = f":{key}"
                    update_expression += f"{attr_name} = {attr_value}, "
                    expression_names[attr_name] = key
                    expression_values[attr_value] = value

            # Remove trailing comma
            update_expression = update_expression.rstrip(", ")

            response = self.users_table.update_item(
                Key={
                    'PK': f'USER#{user_id}',
                    'SK': 'PROFILE'
                },
                UpdateExpression=update_expression,
                ExpressionAttributeNames=expression_names,
                ExpressionAttributeValues=expression_values,
                ReturnValues='ALL_NEW'
            )

            item = response['Attributes']
            return User(
                user_id=item.get('user_id'),
                name=item.get('name'),
                email=item.get('email'),
                phone=item.get('phone'),
                balance=int(item.get('balance', 0)),
                notify_channel=NotifyChannel(item.get('notify_channel'))
            )

        except ClientError as e:
            raise Exception(
                f"Error updating user: {e.response['Error']['Message']}"
            )
