from flask import request, jsonify, render_template, redirect, url_for, session
from flask_jwt_extended import jwt_required, get_jwt_identity
from . import event_bp
from app.models.event import Event
from app.models.participant import Participant
from app.models.user import User
from app.models.archived_event import archive_events
from app.utils.email_notifications import (
    send_event_registration_successful_notification, 
    send_event_updated_notification, 
    send_event_deleted_notification
)
import uuid
import datetime

@event_bp.route('/create', methods=['GET','POST'])
@jwt_required()
def create_event():
    if request.method == 'GET':
        return render_template('create_event.html')
    event_id = str(uuid.uuid4())
    user_id = get_jwt_identity()
    data = request.form.to_dict()
    recurrence = data.get('recurrence', None)
    end_recurrence = data.get('end_recurrence', None)
    try:
        event_datetime = datetime.datetime.strptime(data['datetime'], '%Y-%m-%dT%H:%M')
        if end_recurrence:
            end_recurrence = datetime.datetime.strptime(data['end_recurrence'], '%Y-%m-%dT%H:%M')
    except ValueError:
        return jsonify({'error': 'Invalid datetime format. Use ISO 8601 format: YYYY-MM-DDTHH:MM'}), 400
    if not data.get('participants'):
        participants = []
    else:
        participants = data.get('participants', '').split(',')
    if any([not Participant.get(participant) for participant in participants]):
        return jsonify({'error': 'One or more participants do not exist. Please register first'}), 400
    if any([param not in data for param in ['name', 'description', 'location', 'category']]):
        return jsonify({'error': "Invalid Request. All of ('name', 'description', 'location', 'category') are mandatory"}), 400
    if recurrence and not end_recurrence:
        return jsonify({'error': 'recurrence and end_recurrence both must be specified'}), 400
    if recurrence and recurrence not in ['weekly', 'daily', 'monthly']:
        return jsonify({'error': "recurrence should be any of ('weekly', 'daily', 'monthly')"}), 400
    event = {
        'EventID': event_id,
        'EventName': data['name'],
        'Description': data['description'],
        'EventDateTime': event_datetime.strftime('%Y-%m-%dT%H:%M:%SZ'),
        'EventLocation': data.get('location', ''),
        'Participants': participants,
        'OrganizerID': user_id,
        'Feedback': [],
        'Category': data['category'],
        'Recurrence': recurrence,
        'EndRecurrence': end_recurrence.strftime('%Y-%m-%dT%H:%M:%SZ') if end_recurrence else None,
    }
    Event.create(event)
    User.add_organized_event(user_id, event_id)
    for participant in participants:
        try:
            p = Participant.get(participant)
            send_event_updated_notification(event, p['Email'], p['ParticipantName'])
        except:
            pass
    return redirect(url_for('event_bp.list_events'))

@event_bp.route('/category/<category>', methods=['GET'])
@jwt_required()
def get_events_by_category(category):
    events = Event.get_by_category(category)
    return render_template('list_events.html', events=events)

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
        return render_template('view_event.html', event=event)
    else:
        return jsonify({'error': 'Event not found'}), 404

@event_bp.route('/', methods=['GET'])
@jwt_required()
def list_events():
    events = Event.list()
    return render_template('list_events.html', events=events)

@event_bp.route('/<event_id>/update', methods=['GET', 'POST'])
@jwt_required()
def update_event(event_id):
    data = request.form.to_dict()
    if not event_id:
        return jsonify({'error': 'EventID invalid'}), 400
    event = Event.get(event_id)
    if not event:
        return jsonify({'error': 'Event not found'}), 404
    if request.method =='GET':
        return render_template('update_event.html', event=event)
    if not data.get('participants'):
        participants = []
    else:
        participants = data.get('participants', '').split(',')
    if any([not Participant.get(participant) for participant in participants]):
        return jsonify({'error': 'One or more participants do not exist. Please register first'}), 400
    event_datetime = data.get('datetime')
    if event_datetime:
        try:
            event_datetime = datetime.datetime.strptime(data['datetime'], '%Y-%m-%dT%H:%M')
        except ValueError:
            return jsonify({'error': 'Invalid datetime format. Use ISO 8601 format: YYYY-MM-DDTHH:MM'}), 400
    event_update = {
        'EventName': data.get('name', event.get('EventName')),
        'Description': data.get('description', event["Description"]),
        'EventDateTime': event_datetime.strftime('%Y-%m-%dT%H:%M:%SZ') if event_datetime else event["EventDateTime"],
        'EventLocation': data.get('location', event["EventLocation"]),
        'Participants': participants if participants else event["Participants"]
    }
    Event.update(event_id, event_update)
    for participant in participants:
        try:
            p = Participant.get(participant)
            send_event_updated_notification(event_update, p['Email'], p['ParticipantName'])
        except:
            pass
    return redirect(url_for('event_bp.get_event', event_id=event_id))

@event_bp.route('/<event_id>/feedback', methods=['POST'])
@jwt_required()
def add_feedback(event_id):
    data = request.form.to_dict()
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
    if int(data.get('rating')) < 1 or int(data.get('rating')) > 5:
        return jsonify({'error': 'Rating should be between 1 and 5'}), 400
    feedback = {
        'ParticipantID': participant_id,
        'Rating': data['rating'],
        'Comment': data['comment']
    }
    feedback_entries = Event.add_feedback(event_id, feedback)
    if feedback_entries is None:
        return jsonify({'error': 'Event not found'}), 404

    return jsonify({'message': 'Feedback added successfully', 'feedback': feedback_entries})

@event_bp.route('/<event_id>/register', methods=['POST'])
@jwt_required()
def register_participant(event_id):
    data = request.form.to_dict()
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
        send_event_registration_successful_notification(event, participant['Email'], participant['ParticipantName'])
    except:
        pass

    return redirect(url_for('event_bp.get_event', event_id=event_id))

@event_bp.route('/<event_id>/delete', methods=['GET'])
@jwt_required()
def delete_event(event_id):
    if not event_id:
        return jsonify({'error': 'EventID invalid'}), 400
    event = Event.get(event_id)
    if not event:
        return jsonify({'error': 'Event not found'}), 404
    Event.delete(event_id)
    for participant in event['Participants']:
        p = Participant.get(participant)
        send_event_deleted_notification(event, p['Email'], p['ParticipantName'])
    return redirect(url_for('event_bp.list_events'))
