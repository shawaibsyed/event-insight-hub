from . import dynamodb
from flask_bcrypt import Bcrypt

user_table = dynamodb.Table('User')
bcrypt = Bcrypt()

class User:
    @staticmethod
    def create(user):
        user['HashedPassword'] = bcrypt.generate_password_hash(user['HashedPassword']).decode('utf-8')
        user_table.put_item(Item=user)
    
    @staticmethod
    def get(user_id):
        response = user_table.get_item(Key={'UserID': user_id})
        return response.get('Item')
    
    @staticmethod
    def get_by_username(username):
        response = user_table.scan(
            FilterExpression="Username = :username",
            ExpressionAttributeValues={":username": username}
        )
        items = response.get('Items', [])
        if items:
            return items[0]
        return None

    @staticmethod
    def list():
        response = user_table.scan()
        return response.get('Items', [])
    
    @staticmethod
    def update(user_id, updates):
        update_expression = "set "
        expression_attribute_values = {}
        for key, value in updates.items():
            if key == 'HashedPassword':
                value = bcrypt.generate_password_hash(value).decode('utf-8')
            update_expression += f"{key} = :{key}, "
            expression_attribute_values[f":{key}"] = value
        update_expression = update_expression.rstrip(", ")
        
        user_table.update_item(
            Key={'UserID': user_id},
            UpdateExpression=update_expression,
            ExpressionAttributeValues=expression_attribute_values
        )
    
    @staticmethod
    def delete(user_id):
        user_table.delete_item(Key={'UserID': user_id})
    
    @staticmethod
    def check_password(hashed_password, plain_password):
        return bcrypt.check_password_hash(hashed_password, plain_password)

    @classmethod
    def add_organized_event(cls, user_id, event_id):
        organizer = cls.get(user_id)
        if not organizer:
            return None

        events_organized = organizer.get('OrganizedEvents', [])
        if event_id not in events_organized:
            events_organized.append(event_id)

        cls.update(user_id, {'OrganizedEvents': events_organized})
