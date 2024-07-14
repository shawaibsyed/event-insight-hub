from flask import request, jsonify
from . import participant_bp
from flask_jwt_extended import jwt_required
from app.models.participant import Participant
import uuid
from flask_request_validator import (
    Param,
    validate_params,
    ValidRequest,
    JSON,
    GET,
    PATH
)

@participant_bp.route('/', methods=['POST'])
@validate_params(
    Param('name', JSON, str, required=True),
    Param('email', JSON, str,  required=True),
)
def create_participant(valid: ValidRequest):
    participant_id = str(uuid.uuid4())
    data = valid.get_json()
    participant = {
        'ParticipantID': participant_id,
        'ParticipantName': data['name'],
        'Email': data['email'],
        'EventsAttended': []
    }
    Participant.create(participant)
    return jsonify(participant), 201

@participant_bp.route('/<participant_id>', methods=['GET'])
@validate_params(
    Param('participant_id', PATH, str, required=True),
)
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
@validate_params(
    Param('name', JSON, str, required=False),
    Param('email', JSON, str,  required=False),
    Param('participant_id', PATH, str, required=True)
)
def update_participant(participant_id, valid: ValidRequest):
    if not participant_id:
        return jsonify({'error': 'ParticipantID invalid'}), 400
    if not Participant.get(participant_id):
        return jsonify({'error': 'Participant not found'}), 404
    data = valid.get_json()
    participant = {
        'ParticipantName': data['name'],
        'Email': data['email']
    }
    Participant.update(participant_id, participant)
    return jsonify({'message': 'Participant updated successfully'})

@participant_bp.route('/<participant_id>', methods=['DELETE'])
@validate_params(
    Param('participant_id', PATH, str, required=True),
)
@jwt_required()
def delete_participant(participant_id):
    Participant.delete(participant_id)
    return jsonify({'message': 'Participant deleted successfully'})

@participant_bp.route('/search', methods=['GET'])
@jwt_required()
@validate_params(
    Param('email',GET, str,  required=True),
)
def search_participant():
    email = request.args.get('email')
    if not email:
        return jsonify({'error': 'Email query parameter is required'}), 400

    participants = Participant.get_by_email(email)
    if participants:
        return jsonify(participants)
    else:
        return jsonify({'error': 'Participant not found'}), 404
