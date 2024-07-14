import pytest
from app import create_app
from app.models.participant import register_participant, get_participant

@pytest.fixture
def app():
    app = create_app()
    app.config['TESTING'] = True
    return app

@pytest.fixture
def client(app):
    return app.test_client()

def test_register_participant(client):
    participant_data = {
        'ParticipantID': '1',
        'Name': 'Test Participant',
        'Email': 'test@example.com'
    }
    response = client.post('/participants', json=participant_data)
    assert response.status_code == 200
    assert b'Test Participant' in response.data

def test_get_participant(client):
    participant_id = '1'
    response = client.get(f'/participants/{participant_id}')
    assert response.status_code == 200
    assert b'Test Participant' in response.data