import boto3
import os
from botocore.exceptions import ClientError
from app.domain.models.fund import Fund
from app.application.ports.funds import FundPort
from typing import List, Tuple, Dict, Any


class FundAdapter(FundPort):
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

        self.funds_table = self.dynamodb.Table('AppChallenge')

    def get_by_id(self, fund_id: str) -> Fund:
        """Get a fund by its ID."""
        try:
            response = self.funds_table.get_item(
                Key={
                    'PK': f'FUND#{fund_id}',
                    'SK': 'PROFILE'
                }
            )

            if 'Item' not in response:
                raise ValueError(f"Fund with ID {fund_id} not found")

            item = response['Item']
            return Fund(
                fund_id=item.get('fund_id'),
                name=item.get('name'),
                min_amount=float(item.get('min_amount', 0)),
                category=item.get('category')
            )
        except ClientError as e:
            raise Exception(
                f"Error retrieving fund: {e.response['Error']['Message']}"
            )

    def list_all(
        self,
        limit: int = 50,
        last_key: str | None = None
    ) -> Tuple[List[Fund], str | None]:
        """List all funds."""
        try:
            scan_kwargs: Dict[str, Any] = {'Limit': limit}

            if last_key:
                scan_kwargs['ExclusiveStartKey'] = {'fund_id': last_key}

            response = self.funds_table.scan(**scan_kwargs)

            funds = []
            for item in response.get('Items', []):
                fund = Fund(
                    fund_id=item['fund_id'],
                    name=item['name'],
                    min_amount=float(item['min_amount']),
                    category=item['category']
                )
                funds.append(fund)

            next_key = None
            if 'LastEvaluatedKey' in response:
                next_key = response['LastEvaluatedKey']['fund_id']

            return (funds, next_key)

        except ClientError as e:
            raise Exception(
                f"Error listing funds: {e.response['Error']['Message']}"
            )
