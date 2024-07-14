from flask import request, jsonify
from flask_jwt_extended import jwt_required, get_jwt_identity
from . import event_bp
from app.models.event import Event
from app.models.participant import Participant
from app.models.user import User
from flask_request_validator import (
    Param,
    validate_params,
    ValidRequest,
    JSON,
    PATH
)
import uuid
import datetime

@event_bp.route('/', methods=['POST'])
@jwt_required()
@validate_params(
    Param('name', JSON, str, required=True),
    Param('description', JSON, str, required=True),
    Param('dateTime', JSON, str, required=True),
    Param('location', JSON, str, required=True),
)
def create_event(valid: ValidRequest):
    event_id = str(uuid.uuid4())
    user_id = get_jwt_identity()
    data = valid.get_json()
    try:
        event_datetime = datetime.strptime(data['dateTime'], '%Y-%m-%dT%H:%M:%SZ').strftime("%Y-%m-%dT%H:%M:%SZ")
    except ValueError:
        return jsonify({'error': 'Invalid datetime format. Use ISO 8601 format: YYYY-MM-DDTHH:MM:SSZ'}), 400
    participants = data.get('participants', [])
    if any([not Participant.get(participant) for participant in participants]):
        return jsonify({'error': 'One or more participant do not exist. Please register first'}), 400
    event = {
        'EventID': event_id,
        'Name': data['name'],
        'Description': data['description'],
        'EventDateTime': event_datetime,
        'EventLocation': data.get('location', ''),
        'Participants': participants,
        'OrganizerID': user_id,
        'Feedback': []
    }
    Event.create(event)
    User.add_organized_event(user_id, event_id)
    return jsonify(event), 201

@event_bp.route('/<event_id>', methods=['GET'])
@jwt_required()
@validate_params(
    Param('event_id', PATH, str, required=True),
)
def get_event(event_id):
    if not event_id:
        return jsonify({'error': 'EventID invalid'}), 400
    event = Event.get(event_id)
    if event:
        return jsonify(event)
    else:
        return jsonify({'error': 'Event not found'}), 404

@event_bp.route('/', methods=['GET'])
@jwt_required()
def list_events():
    events = Event.list()
    return jsonify(events)

@event_bp.route('/<event_id>', methods=['PUT'])
@jwt_required()
@validate_params(
    Param('name', JSON, str, required=False),
    Param('description', JSON, str, required=False),
    Param('dateTime', JSON, str, required=False),
    Param('location', JSON, str, required=False),
    Param('event_id', PATH, str, required=True),
)
def update_event(event_id, valid: ValidRequest):
    data = valid.get_json()
    if not event_id:
        return jsonify({'error': 'EventID invalid'}), 400
    if not Event.get(event_id):
        return jsonify({'error': 'Event not found'}), 404
    participants = data.get('participants', [])
    if any([not Participant.get(participant) for participant in participants]):
        return jsonify({'error': 'One or more participant do not exist. Please register first'}), 400
    try:
        event_datetime = datetime.strptime(data['dateTime'], '%Y-%m-%dT%H:%M:%SZ').strftime("%Y-%m-%dT%H:%M:%SZ")
    except ValueError:
        return jsonify({'error': 'Invalid datetime format. Use ISO 8601 format: YYYY-MM-DDTHH:MM:SSZ'}), 400
    event = {
        'EventName': data['name'],
        'Description': data['description'],
        'EventDateTime': event_datetime,
        'EventLocation': data.get('location', ''),
        'Participants': participants
    }
    Event.update(event_id, event)
    return jsonify({'message': 'Event updated successfully'})

@event_bp.route('/<event_id>/feedback', methods=['POST'])
@jwt_required()
@validate_params(
    Param('rating', JSON, int, required=True),
    Param('comment', JSON, str, required=True),
    Param('event_id', PATH, str, required=True),
)
def add_feedback(event_id,valid: ValidRequest):
    data = valid.get_json()
    participant_id = data.get('participant_id')
    if not participant_id:
        return jsonify({'error': 'Participant ID is required'}), 400
    participant = Participant.get(participant_id)
    if not participant:
        return jsonify({'error': 'Participant does not exist'}), 400
    if not event_id:
        return jsonify({'error': 'EventID invalid'}), 400
    if not Event.get(event_id):
        return jsonify({'error': 'Event not found'}), 404
    if data.get('rating') < 1 and data.get('rating') > 5:
        return jsonify({'error': 'Rating should be greater than 1 and less than 5'}), 400
    feedback = {
        'ParticipantID': participant_id,
        'Rating': data.get('rating'),
        'Comment': data.get('comment')
    }
    feedback_entries = Event.add_feedback(event_id, feedback)
    if feedback_entries is None:
        return jsonify({'error': 'Event not found'}), 404

    return jsonify({'message': 'Feedback added successfully', 'feedback': feedback_entries})

@event_bp.route('/<event_id>/register', methods=['POST'])
@jwt_required()
@validate_params(
    Param('participant_id', JSON, str, required=True),
    Param('event_id', PATH, str, required=True),
)
def register_participant(event_id, valid: ValidRequest):
    data = valid.get_json()
    if not event_id:
        return jsonify({'error': 'EventID invalid'}), 400
    if not Event.get(event_id):
        return jsonify({'error': 'Event not found'}), 404
    participant_id = data.get('participant_id')
    if not participant_id:
        return jsonify({'error': 'Participant ID is required'}), 400
    participant = Participant.get(participant_id)
    if not participant:
        return jsonify({'error': 'Participant does not exist. Please register first'}), 400
    participants = Event.register_participant(event_id, participant_id)
    Participant.register_event(participant_id, event_id)

    return jsonify({'message': 'Participant registered successfully', 'participants': participants})

@event_bp.route('/<event_id>', methods=['DELETE'])
@jwt_required()
@validate_params(
    Param('event_id', PATH, str, required=True),
)
def delete_event(event_id):
    Event.delete(event_id)
    return jsonify({'message': 'Event deleted successfully'})
