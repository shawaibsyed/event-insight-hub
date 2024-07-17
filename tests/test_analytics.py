import pytest
from flask import json
from unittest.mock import patch
from run import app
from flask_jwt_extended import create_access_token
import numpy

@pytest.fixture
def client():
    with app.test_client() as client:
        with app.app_context():
            yield client

@patch('app.analytics.event_analytics.events_per_month')
@patch('flask_jwt_extended.get_jwt_identity')
def test_get_events_per_month(mock_jwt_identity, mock_events_per_month, client):
    mock_jwt_identity.return_value = 'user123'
    user_id = 'user123'
    access_token = create_access_token(identity=user_id)
    headers = {
        'Authorization': f'Bearer {access_token}'
    }

    mock_events_per_month.return_value = {"2024-07": "3"}
    response = client.get('/analytics/events-per-month', headers=headers)
    assert response.status_code == 200
    assert response.get_json() == {"2024-07": "3"}

@patch('app.analytics.event_analytics.events_per_organizer')
@patch('flask_jwt_extended.get_jwt_identity')
def test_get_events_per_organizer(mock_jwt_identity, mock_events_per_organizer, client):
    mock_jwt_identity.return_value = 'user123'
    user_id = 'user123'
    access_token = create_access_token(identity=user_id)
    headers = {
        'Authorization': f'Bearer {access_token}'
    }

    mock_events_per_organizer.return_value = {"ebd577af-35e8-4433-b5ca-9b3b82991d75": 3}
    response = client.get('/analytics/events-per-organizer', headers=headers)
    assert response.status_code == 200
    assert response.get_json() == {"ebd577af-35e8-4433-b5ca-9b3b82991d75": 3}

@patch('app.analytics.participant_analytics.participants_events_attended')
@patch('flask_jwt_extended.get_jwt_identity')
def test_get_participants_events_attended(mock_jwt_identity, mock_participants_events_attended, client):
    mock_jwt_identity.return_value = 'user123'
    user_id = 'user123'
    access_token = create_access_token(identity=user_id)
    headers = {
        'Authorization': f'Bearer {access_token}'
    }

    mock_participants_events_attended.return_value = {"25%": 0.0,"50%": 1.0,"75%": 1.0,"count": 5.0,"max": 1.0,"mean": 0.6,"min": 0.0,"std": 0.5477225575051662}
    response = client.get('/analytics/participants-events-attended', headers=headers)
    assert response.status_code == 200
    assert response.get_json() == {"25%": 0.0,"50%": 1.0,"75%": 1.0,"count": 5.0,"max": 1.0,"mean": 0.6,"min": 0.0,"std": 0.5477225575051662}
