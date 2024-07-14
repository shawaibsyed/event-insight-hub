from . import dynamodb
import uuid

event_table = dynamodb.Table('Event')

class Event:
    @staticmethod
    def create(event):
        event_table.put_item(Item=event)
    
    @staticmethod
    def get(event_id):
        response = event_table.get_item(Key={'EventID': event_id})
        return response.get('Item')
    
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
