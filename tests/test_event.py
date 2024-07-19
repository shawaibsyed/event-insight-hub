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

@patch('app.models.event.Event.create')
@patch('app.models.user.User.add_organized_event')
@patch('app.models.participant.Participant.get')
@patch('flask_jwt_extended.get_jwt_identity')
def test_create_event_success(mock_jwt_identity, mock_participant_get, mock_add_organized_event, mock_event_create, client):
    mock_jwt_identity.return_value = 'user123'
    mock_participant_get.return_value = True
    mock_event_create.return_value = None
    user_id = 'user123'
    access_token = create_access_token(identity=user_id)
    headers = {
        'Authorization': f'Bearer {access_token}'
    }

    response = client.post('/events/', json={
        'name': 'New Event',
        'description': 'Event Description',
        'dateTime': '2023-01-01T00:00:00Z',
        'end_recurrence': '2023-01-10T00:00:00Z',
        'participants': ['participant1'],
        'location': 'Location',
        'category': 'Category',
        'recurrence': 'daily'
    }, headers=headers)
    assert response.status_code == 201
    assert 'New Event' in response.get_json()['EventName']

@patch('flask_jwt_extended.get_jwt_identity')
def test_create_event_invalid_data(mock_jwt_identity, client):
    mock_jwt_identity.return_value = 'user123'
    user_id = 'user123'
    access_token = create_access_token(identity=user_id)
    headers = {
        'Authorization': f'Bearer {access_token}'
    }

    response = client.post('/events/', json={
        'name': 'Incomplete Event',
        'dateTime': '2023-01-01T00:00:00Z',
        'end_recurrence': '2023-01-10T00:00:00Z',
        # Missing other mandatory fields
    }, headers=headers)
    assert response.status_code == 400
    assert 'Invalid Request' in response.get_json()['error']

@patch('app.models.event.Event.get')
@patch('flask_jwt_extended.get_jwt_identity')
def test_get_event_success(mock_jwt_identity, mock_event_get, client):
    mock_jwt_identity.return_value = 'user123'
    mock_event_get.return_value = {'EventID': '1', 'EventName': 'Sample Event'}
    user_id = 'user123'
    access_token = create_access_token(identity=user_id)
    headers = {
        'Authorization': f'Bearer {access_token}'
    }

    response = client.get('/events/1', headers=headers)
    assert response.status_code == 200
    assert 'Sample Event' in response.get_json()['EventName']

@patch('app.models.event.Event.list')
@patch('flask_jwt_extended.get_jwt_identity')
def test_list_events_success(mock_jwt_identity, mock_event_list, client):
    mock_jwt_identity.return_value = 'user123'
    user_id = 'user123'
    access_token = create_access_token(identity=user_id)
    mock_event_list.return_value = [{'EventID': '1', 'EventName': 'Sample Event'}]
    headers = {
        'Authorization': f'Bearer {access_token}'
    }

    response = client.get('/events/', headers=headers)
    assert response.status_code == 200
    assert len(response.get_json()) == 1

@patch('app.models.event.Event.update')
@patch('app.models.event.Event.get')
@patch('flask_jwt_extended.get_jwt_identity')
def test_update_event_success(mock_jwt_identity, mock_event_get, mock_event_update, client):
    mock_jwt_identity.return_value = 'user123'
    user_id = 'user123'
    access_token = create_access_token(identity=user_id)
    mock_event_get.return_value = {'EventID': '1', 'EventName': 'Old Event'}
    headers = {
        'Authorization': f'Bearer {access_token}'
    }

    response = client.put('/events/1', json={
        'name': 'Updated Event',
        'description': 'Updated Description'
    }, headers=headers)
    assert response.status_code == 200
    assert 'Event updated successfully' in response.get_json()['message']

@patch('app.models.event.Event.delete')
@patch('app.models.event.Event.get')
@patch('app.models.participant.Participant.get')
@patch('flask_jwt_extended.get_jwt_identity')
def test_delete_event_success(mock_jwt_identity, mock_participant_get, mock_event_get, mock_event_delete, client):
    user_id = 'user123'
    mock_jwt_identity.return_value = user_id
    mock_event_get.return_value = {'EventID': '1', 'EventName': 'Sample Event', 'Participants': ['2']}
    mock_event_delete.return_value = None
    mock_participant_get.return_value = {'ParticipantID': '2', 'ParticipantName': 'Participant', 'Email': 'test@example.com'}

    access_token = create_access_token(identity=user_id)
    headers = {
        'Authorization': f'Bearer {access_token}'
    }

    response = client.delete('/events/1', headers=headers)
    assert response.status_code == 200
    assert 'Event deleted successfully' in response.get_json()['message']
