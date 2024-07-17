from flask import request, jsonify
from . import participant_bp
from flask_jwt_extended import jwt_required
from app.models.participant import Participant
from app.utils.email_notifications import send_participant_registration_successful_notification
import uuid

@participant_bp.route('/', methods=['POST'])
def create_participant():
    participant_id = str(uuid.uuid4())
    data = request.get_json()
    if not data.get('name') or not data.get('email'):
        return jsonify({'error': 'Invalid Request, name or email missing'}), 400
    participant = {
        'ParticipantID': participant_id,
        'ParticipantName': data['name'],
        'Email': data['email'],
        'EventsAttended': []
    }
    Participant.create(participant)
    try:
        send_participant_registration_successful_notification(participant.get("Email"), participant.get("ParticipantName"))
    except:
        pass
    return jsonify(participant), 201

@participant_bp.route('/<participant_id>', methods=['GET'])
@jwt_required()
def get_participant(participant_id):
    if not participant_id:
        return jsonify({'error': 'ParticipantID invalid'}), 400
    participant = Participant.get(participant_id)
    if participant:
        return jsonify(participant)
    else:
        return jsonify({'error': 'Participant not found'}), 404

@participant_bp.route('/', methods=['GET'])
@jwt_required()
def list_participants():
    participants = Participant.list()
    return jsonify(participants)

@participant_bp.route('/<participant_id>', methods=['PUT'])
@jwt_required()
def update_participant(participant_id):
    if not participant_id:
        return jsonify({'error': 'ParticipantID invalid'}), 400
    if not Participant.get(participant_id):
        return jsonify({'error': 'Participant not found'}), 404
    data = request.get_json()
    if not data['name'] or not data['email']:
        return jsonify({'error': 'Invalid Request, name or email missing'}), 400
    participant = {
        'ParticipantName': data['name'],
        'Email': data['email']
    }
    Participant.update(participant_id, participant)
    return jsonify({'message': 'Participant updated successfully'})

@participant_bp.route('/<participant_id>', methods=['DELETE'])
@jwt_required()
def delete_participant(participant_id):
    if not participant_id:
        return jsonify({'error': 'ParticipantID invalid'}), 400
    Participant.delete(participant_id)
    return jsonify({'message': 'Participant deleted successfully'})

@participant_bp.route('/search', methods=['GET'])
@jwt_required()
def search_participant():
    email = request.args.get('email')
    if not email:
        return jsonify({'error': 'Email query parameter is required'}), 400

    participants = Participant.get_by_email(email)
    if participants:
        return jsonify(participants)
    else:
        return jsonify({'error': 'Participant not found'}), 404
