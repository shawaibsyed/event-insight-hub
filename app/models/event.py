from . import dynamodb
import uuid
import datetime
from boto3.dynamodb.conditions import Key

event_table = dynamodb.Table('Event')

# Helper function to generate recurring events
def generate_recurring_events(event, recurrence, end_recurrence):
    events = []
    current_datetime = datetime.datetime.strptime(event['EventDateTime'], '%Y-%m-%dT%H:%M:%SZ')
    end_datetime = datetime.datetime.strptime(end_recurrence, '%Y-%m-%dT%H:%M:%SZ')

    while current_datetime <= end_datetime:
        new_event = event.copy()
        new_event['EventID'] = str(uuid.uuid4())
        new_event['EventDateTime'] = current_datetime.strftime('%Y-%m-%dT%H:%M:%SZ')
        events.append(new_event)

        if recurrence == 'daily':
            current_datetime += datetime.timedelta(days=1)
        elif recurrence == 'weekly':
            current_datetime += datetime.timedelta(weeks=1)
        elif recurrence == 'monthly':
            current_datetime += datetime.timedelta(weeks=4)  # Simplified monthly recurrence

    return events

class Event:
    def __init__(self, name, description, datetime, location, organizer_id, category, recurrence, end_recurrence):
        self.event_id = str(uuid.uuid4())
        self.name = name
        self.description = description
        self.datetime = datetime
        self.location = location
        self.organizer_id = organizer_id
        self.participants = []
        self.feedback = []
        self.category = category
        self.recurrence = recurrence
        self.end_recurrence = end_recurrence

    def to_dict(self):
        return {
            'EventID': self.event_id,
            'EventName': self.name,
            'Description': self.description,
            'EventDateTime': self.datetime,
            'EventLocation': self.location,
            'OrganizerID': self.organizer_id,
            'Participants': self.participants,
            'Feedback': self.feedback,
            'Category': self.category,
            'Recurrence': self.recurrence,
            'EndRecurrence': self.end_recurrence
        }

    @staticmethod
    def create(event):
        if event['Recurrence'] and event['EndRecurrence']:
            recurring_events = generate_recurring_events(event, event['Recurrence'], event['EndRecurrence'])
            with event_table.batch_writer() as batch:
                for e in recurring_events:
                    batch.put_item(Item=e)
        else:
            event_table.put_item(Item=event)
    
    @staticmethod
    def get(event_id):
        response = event_table.get_item(Key={'EventID': event_id})
        return response.get('Item')
    
    @staticmethod
    def get_by_category(category):
        event_table = dynamodb.Table('Event')
        response = event_table.scan(
            FilterExpression=Key('Category').eq(category)
        )
        return response.get('Items', [])
    
    @staticmethod
    def list():
        response = event_table.scan()
        return response.get('Items', [])
    
    @staticmethod
    def update(event_id, updates):
        update_expression = "set "
        expression_attribute_values = {}
        for key, value in updates.items():
            update_expression += f"{key} = :{key}, "
            expression_attribute_values[f":{key}"] = value
        update_expression = update_expression.rstrip(", ")
        
        event_table.update_item(
            Key={'EventID': event_id},
            UpdateExpression=update_expression,
            ExpressionAttributeValues=expression_attribute_values
        )
    
    @staticmethod
    def delete(event_id):
        event_table.delete_item(Key={'EventID': event_id})

    @classmethod
    def register_participant(cls, event_id, participant_id):
        event = cls.get(event_id)
        if not event:
            return None

        participants = event.get('Participants', [])
        if participant_id not in participants:
            participants.append(participant_id)

        cls.update(event_id, {'Participants': participants})
        return participants

    @classmethod
    def add_feedback(cls, event_id, feedback):
        event = cls.get(event_id)
        if not event:
            return None

        feedback_entries = event.get('Feedback', [])
        feedback_id = str(uuid.uuid4())
        feedback['FeedbackID'] = feedback_id
        feedback_entries.append(feedback)

        cls.update(event_id, {'Feedback': feedback_entries})
        return feedback_entries
