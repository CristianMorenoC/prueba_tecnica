#!/usr/bin/env python3

# Test script para verificar que el servicio maneja los eventos reales correctamente

from main import lambda_handler

# Evento real de creación de usuario
user_profile_event = {
    'Records': [
        {
            'eventID': 'e61abe6bd5ad73862e63e6213cc4aebd',
            'eventName': 'INSERT',
            'eventVersion': '1.1',
            'eventSource': 'aws:dynamodb',
            'awsRegion': 'us-east-1',
            'dynamodb': {
                'ApproximateCreationDateTime': 1755887881.0,
                'Keys': {
                    'SK': {'S': 'PROFILE'},
                    'PK': {'S': 'USER#005'}
                },
                'NewImage': {
                    'notification_channel': {'S': 'email'},
                    'balance': {'N': '600000'},
                    'phone': {'S': '+573007586230'},
                    'user_id': {'S': 'u003'},
                    'SK': {'S': 'PROFILE'},
                    'name': {'S': 'Cristian Luis Salamanca'},
                    'PK': {'S': 'USER#0003'},
                    'email': {'S': 'cristianfmoreno95@gmail.com'}
                },
                'SequenceNumber': '3914200004048040612420311',
                'SizeBytes': 152,
                'StreamViewType': 'NEW_AND_OLD_IMAGES'
            },
            'eventSourceARN': 'arn:aws:dynamodb:us-east-1:596727820170:table/amaris-consulting-AppChallenge-X4BFAICDBIJT/stream/2025-08-22T17:53:02.346'
        }
    ]
}

# Evento real de suscripción
subscription_event = {
    'Records': [
        {
            'eventID': '1a1ccf48670c90aba91490913a1f5d8b',
            'eventName': 'INSERT',
            'eventVersion': '1.1',
            'eventSource': 'aws:dynamodb',
            'awsRegion': 'us-east-1',
            'dynamodb': {
                'ApproximateCreationDateTime': 1755888148.0,
                'Keys': {
                    'SK': {'S': 'SUB#f001'},
                    'PK': {'S': 'USER#u007'}
                },
                'NewImage': {
                "PK": {"S": "USER#u007"},
                "SK": {"S": "SUB#f001"},
                "user_id": {"S": "u007"},
                "fund_id": {"S": "f001"},
                "amount": {"N": "100000"},
                "status": {"S": "active"},
                "created_at": {"S": "2025-08-20T10:00:00Z"},
                "cancelled_at": {"NULL": True},
                "notification_channel": {"S": "email"}
                },
                'SequenceNumber': '3931300000459376624562377',
                'SizeBytes': 146,
                'StreamViewType': 'NEW_AND_OLD_IMAGES'
            },
            'eventSourceARN': 'arn:aws:dynamodb:us-east-1:596727820170:table/amaris-consulting-AppChallenge-X4BFAICDBIJT/stream/2025-08-22T17:53:02.346'
        }
    ]
}

if __name__ == "__main__":
    '''print("Testing User Profile Event:")
    try:
        result = lambda_handler(user_profile_event, None)
        print(f"Result: {result}")
    except Exception as e:
        print(f"Error: {e}")
    
    print("\n" + "="*50 + "\n")
    '''
 
    print("Testing Subscription Event:")
    try:
        result = lambda_handler(subscription_event, None)
        print(f"Result: {result}")
    except Exception as e:
        print(f"Error: {e}")
    