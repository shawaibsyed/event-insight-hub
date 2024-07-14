from . import dynamodb
import boto3

participant_table = dynamodb.Table('Participant')

class Participant:
    @staticmethod
    def create(participant):
        participant_table.put_item(Item=participant)
    
    @staticmethod
    def get(participant_id):
        response = participant_table.get_item(Key={'ParticipantID': participant_id})
        return response.get('Item')
    
    @staticmethod
    def list():
        response = participant_table.scan()
        return response.get('Items', [])
    
    @staticmethod
    def update(participant_id, updates):
        update_expression = "set "
        expression_attribute_values = {}
        for key, value in updates.items():
            update_expression += f"{key} = :{key}, "
            expression_attribute_values[f":{key}"] = value
        update_expression = update_expression.rstrip(", ")
        
        participant_table.update_item(
            Key={'ParticipantID': participant_id},
            UpdateExpression=update_expression,
            ExpressionAttributeValues=expression_attribute_values
        )
    
    @staticmethod
    def delete(participant_id):
        participant_table.delete_item(Key={'ParticipantID': participant_id})
    
    @classmethod
    def register_event(cls, participant_id, event_id):
        participant = cls.get(participant_id)
        if not participant:
            return None

        events_attended = participant.get('EventsAttended', [])
        if event_id not in events_attended:
            events_attended.append(event_id)

        cls.update(participant_id, {'EventsAttended': events_attended})

    @classmethod
    def get_by_email(cls, email):
        response = participant_table.scan(
            FilterExpression=boto3.dynamodb.conditions.Attr('Email').eq(email)
        )
        return response.get('Items', [])
