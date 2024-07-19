import pytest
from flask import json
from unittest.mock import patch
from run import app
from flask_jwt_extended import create_access_token

@pytest.fixture
def client():
    with app.test_client() as client:
        with app.app_context():  # This line adds the application context
            yield client

@patch('app.models.participant.Participant.create')
@patch('app.utils.email_notifications.send_participant_registration_successful_notification')
def test_create_participant_success(mock_send_notification, mock_create, client):
    mock_send_notification.return_value = None
    mock_create.return_value = {'Participant': 'John Doe', 'Email': 'john@example.com'}
    user_id = 'user123'
    access_token = create_access_token(identity=user_id)
    headers = {
        'Authorization': f'Bearer {access_token}'
    }

    response = client.post('/participants/', json={
        'name': 'John Doe',
        'email': 'john@example.com'
    }, headers=headers)
    assert response.status_code == 201
    assert 'John Doe' in response.get_json()['ParticipantName']

def test_create_participant_missing_data(client):
    user_id = 'user123'
    access_token = create_access_token(identity=user_id)
    headers = {
        'Authorization': f'Bearer {access_token}'
    }

    response = client.post('/participants/', json={
        'name': 'John Doe'
        # Missing email
    }, headers=headers)
    assert response.status_code == 400
    assert 'name or email missing' in response.get_json()['error']

    
@patch('app.models.participant.Participant.get')
def test_get_participant_success(mock_get, client):
    user_id = 'user123'
    access_token = create_access_token(identity=user_id)
    headers = {
        'Authorization': f'Bearer {access_token}'
    }

    mock_get.return_value = {'ParticipantID': '1', 'ParticipantName': 'John Doe'}
    response = client.get('/participants/1', headers=headers)
    assert response.status_code == 200
    assert 'John Doe' in response.get_json()['ParticipantName']

@patch('app.models.participant.Participant.list')
def test_list_participants_success(mock_list, client):
    user_id = 'user123'
    access_token = create_access_token(identity=user_id)
    headers = {
        'Authorization': f'Bearer {access_token}'
    }

    mock_list.return_value = [{'ParticipantID': '1', 'ParticipantName': 'John Doe'}]
    response = client.get('/participants/', headers=headers)
    assert response.status_code == 200
    assert len(response.get_json()) == 1

@patch('app.models.participant.Participant.get_by_email')
def test_search_participant_success(mock_get_by_email, client):
    user_id = 'user123'
    access_token = create_access_token(identity=user_id)
    headers = {
        'Authorization': f'Bearer {access_token}'
    }

    mock_get_by_email.return_value = [{'ParticipantID': '1', 'ParticipantName': 'John Doe'}]
    response = client.get('/participants/search?email=john@example.com', headers=headers)
    assert response.status_code == 200
    assert 'John Doe' in response.get_json()[0]['ParticipantName']
    
@patch('app.models.participant.Participant.update')
@patch('app.models.participant.Participant.get')
def test_update_participant_success(mock_get, mock_update, client):
    user_id = 'user123'
    access_token = create_access_token(identity=user_id)
    headers = {
        'Authorization': f'Bearer {access_token}'
    }

    mock_get.return_value = {'ParticipantID': '1', 'ParticipantName': 'John Doe'}
    response = client.put('/participants/1', json={
        'name': 'Jane Doe',
        'email': 'jane@example.com'
    }, headers=headers)
    assert response.status_code == 200
    assert 'Participant updated successfully' in response.get_json()['message']

@patch('app.models.participant.Participant.delete')
@patch('app.models.participant.Participant.get')
def test_delete_participant_success(mock_get, mock_delete, client):
    user_id = 'user123'
    access_token = create_access_token(identity=user_id)
    headers = {
        'Authorization': f'Bearer {access_token}'
    }

    mock_get.return_value = {'ParticipantID': '1', 'ParticipantName': 'John Doe'}
    response = client.delete('/participants/1', headers=headers)
    assert response.status_code == 200
    assert 'Participant deleted successfully' in response.get_json()['message']