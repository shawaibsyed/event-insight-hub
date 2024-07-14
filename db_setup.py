import boto3
from botocore.exceptions import ClientError

dynamodb = boto3.resource('dynamodb', endpoint_url='http://localhost:8000')

def create_event_table():
    try:
        table = dynamodb.create_table(
            TableName='Event',
            KeySchema=[
                {'AttributeName': 'EventID', 'KeyType': 'HASH'}
            ],
            AttributeDefinitions=[
                {'AttributeName': 'EventID', 'AttributeType': 'S'}
            ],
            ProvisionedThroughput={'ReadCapacityUnits': 5, 'WriteCapacityUnits': 5}
        )
        print("Event table created successfully.")
    except ClientError as e:
        print(e)

def create_user_table():
    try:
        table = dynamodb.create_table(
            TableName='User',
            KeySchema=[
                {'AttributeName': 'UserID', 'KeyType': 'HASH'}
            ],
            AttributeDefinitions=[
                {'AttributeName': 'UserID', 'AttributeType': 'S'}
            ],
            ProvisionedThroughput={'ReadCapacityUnits': 5, 'WriteCapacityUnits': 5}
        )
        print("User table created successfully.")
    except ClientError as e:
        print(e)

def create_participant_table():
    try:
        table = dynamodb.create_table(
            TableName='Participant',
            KeySchema=[
                {'AttributeName': 'ParticipantID', 'KeyType': 'HASH'}
            ],
            AttributeDefinitions=[
                {'AttributeName': 'ParticipantID', 'AttributeType': 'S'}
            ],
            ProvisionedThroughput={'ReadCapacityUnits': 5, 'WriteCapacityUnits': 5}
        )
        print("Participant table created successfully.")
    except ClientError as e:
        print(e)

if __name__ == '__main__':
    create_event_table()
    create_user_table()
    create_participant_table()
