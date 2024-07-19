from . import dynamodb
import datetime
from boto3.dynamodb.conditions import Key

def archive_events():
    event_table = dynamodb.Table('Event')
    archive_table = dynamodb.Table('ArchivedEvent')
    current_datetime = datetime.datetime.utcnow().strftime('%Y-%m-%dT%H:%M:%SZ')

    # Scan for events that have ended
    response = event_table.scan(
        FilterExpression=Key('DateTime').lt(current_datetime)
    )
    past_events = response.get('Items', [])

    with archive_table.batch_writer() as archive_batch, event_table.batch_writer() as event_batch:
        for event in past_events:
            archive_batch.put_item(Item=event)
            event_batch.delete_item(Key={'EventID': event['EventID']})
