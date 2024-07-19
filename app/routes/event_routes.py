from flask import request, jsonify
from flask_jwt_extended import jwt_required, get_jwt_identity
from . import event_bp
from app.models.event import Event
from app.models.participant import Participant
from app.models.user import User
from app.models.archived_event import archive_events
from flask_request_validator import (
    Param,
    validate_params,
    ValidRequest,
    JSON,
    PATH
)
from app.utils.email_notifications import send_event_registration_successful_notification, send_event_updated_notification, send_event_deleted_notification
import uuid
import datetime

@event_bp.route('/', methods=['POST'])
@jwt_required()
def create_event():
    event_id = str(uuid.uuid4())
    user_id = get_jwt_identity()
    data = request.get_json()
    recurrence = data.get('recurrence', None)
    end_recurrence = data.get('end_recurrence', None)
    try:
        event_datetime = datetime.datetime.strptime(data['dateTime'], '%Y-%m-%dT%H:%M:%SZ').strftime('%Y-%m-%dT%H:%M:%SZ')
        end_recurrence = datetime.datetime.strptime(data['end_recurrence'], '%Y-%m-%dT%H:%M:%SZ').strftime('%Y-%m-%dT%H:%M:%SZ')
    except ValueError:
        return jsonify({'error': 'Invalid datetime format. Use ISO 8601 format: YYYY-MM-DDTHH:MM:SSZ'}), 400
    participants = data.get('participants', [])
    if any([not Participant.get(participant) for participant in participants]):
        return jsonify({'error': 'One or more participant do not exist. Please register first'}), 400
    if any([param not in data for param in ['name', 'description', 'location', 'category']]):
        return jsonify({'error': "Invalid Request. All of ('name', 'description', 'location', 'category') are mandatory"}), 400
    if recurrence and not end_recurrence or not recurrence and end_recurrence:
        return jsonify({'error': 'recurrence and end_recurrence both must be specified'}), 400
    if recurrence not in ['weekly', 'daily', 'monthly']:
        return jsonify({'error': "recurrence should be any of ('weekly', 'daily', 'monthly')"}), 400
    event = {
        'EventID': event_id,
        'EventName': data['name'],
        'Description': data['description'],
        'EventDateTime': event_datetime,
        'EventLocation': data.get('location', ''),
        'Participants': participants,
        'OrganizerID': user_id,
        'Feedback': [],
        'Category': data['category'],
        'Recurrence': recurrence,
        'EndRecurrence': end_recurrence,
    }
    Event.create(event)
    User.add_organized_event(user_id, event_id)
    for participant in participants:
        try:
            p = Participant.get(participant)
            send_event_updated_notification(event, p.get('Email'), p.get('ParticipantName'))
        except:
            pass
    return jsonify(event), 201

# Route to get events by category
@event_bp.route('/category/<category>', methods=['GET'])
@jwt_required()
def get_events_by_category(category):
    events = Event.get_by_category(category)
    return jsonify(events), 200

# Route to automatically archive past events
@event_bp.route('/archive', methods=['POST'])
@jwt_required()
def archive_past_events():
    archive_events()
    return jsonify({'message': 'Past events archived successfully'}), 200

@event_bp.route('/<event_id>', methods=['GET'])
@jwt_required()
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
def update_event(event_id):
    data = request.get_json()
    if not event_id:
        return jsonify({'error': 'EventID invalid'}), 400
    event = Event.get(event_id)
    if not event:
        return jsonify({'error': 'Event not found'}), 404
    participants = data.get('participants', [])
    if any([not Participant.get(participant) for participant in participants]):
        return jsonify({'error': 'One or more participant do not exist. Please register first'}), 400
    event_datetime = data.get('dateTime')
    if event_datetime:
        try:
            event_datetime = datetime.datetime.strptime(data['dateTime'], '%Y-%m-%dT%H:%M:%SZ').strftime('%Y-%m-%dT%H:%M:%SZ')
        except ValueError:
            return jsonify({'error': 'Invalid datetime format. Use ISO 8601 format: YYYY-MM-DDTHH:MM:SSZ'}), 400
    participants if participants else event.get("Participants")
    event = {
        'EventName': data.get('name', event.get("EventName")),
        'Description': data.get('description'),
        'EventDateTime': event_datetime if event_datetime else event.get("EventDateTime"),
        'EventLocation': data.get('location', event.get("EventDateTime")),
        'Participants': participants
    }
    Event.update(event_id, event)
    for participant in participants:
        try:
            p = Participant.get(participant)
            send_event_updated_notification(event, p.get('Email'), p.get('ParticipantName'))
        except:
            pass
    return jsonify({'message': 'Event updated successfully'})

@event_bp.route('/<event_id>/feedback', methods=['POST'])
@jwt_required()
def add_feedback(event_id):
    data = request.get_json()
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
    if not data.get('rating') or not data.get('comment'):
        return jsonify({'error': 'Invalid request, rating and comment mandatory'}), 400
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
def register_participant(event_id):
    data = request.get_json()
    if not event_id:
        return jsonify({'error': 'EventID invalid'}), 400
    event = Event.get(event_id)
    if not event:
        return jsonify({'error': 'Event not found'}), 404
    participant_id = data.get('participant_id')
    if not participant_id:
        return jsonify({'error': 'Participant ID is required'}), 400
    participant = Participant.get(participant_id)
    if not participant:
        return jsonify({'error': 'Participant does not exist. Please register first'}), 400
    participants = Event.register_participant(event_id, participant_id)
    Participant.register_event(participant_id, event_id)
    try:
        send_event_registration_successful_notification(event, participant.get("Email"), participant.get("ParticipantName"))
    except:
        pass

    return jsonify({'message': 'Participant registered successfully', 'participants': participants})

@event_bp.route('/<event_id>', methods=['DELETE'])
@jwt_required()
def delete_event(event_id):
    if not event_id:
        return jsonify({'error': 'EventID invalid'}), 400
    event = Event.get(event_id)
    if not event:
        return jsonify({'error': 'Event not found'}), 404
    Event.delete(event_id)
    for participant in event.get('Participants'):
        p = Participant.get(participant)
        send_event_deleted_notification(event, p.get('Email'), p.get('ParticipantName'))
    return jsonify({'message': 'Event deleted successfully'})
