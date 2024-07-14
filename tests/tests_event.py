import pytest
from app import create_app
from app.models.event import create_event, get_event

@pytest.fixture
def app():
    app = create_app()
    app.config['TESTING'] = True
    return app

@pytest.fixture
def client(app):
    return app.test_client()

def test_create_event(client):
    event_data = {
        'EventID': '1',
        'Name': 'Test Event',
        'Description': 'This is a test event',
        'DateTime': '2023-07-13 10:00:00'
    }
    response = client.post('/events', json=event_data)
    assert response.status_code == 200
    assert b'Test Event' in response.data

def test_get_event(client):
    event_id = '1'
    response = client.get(f'/events/{event_id}')
    assert response.status_code == 200
    assert b'Test Event' in response.data
