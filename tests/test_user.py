import pytest
from flask import json
from unittest.mock import patch
from run import app
from flask_jwt_extended import create_access_token

@pytest.fixture
def client():
    with app.test_client() as client:
        with app.app_context():
            yield client

@patch('app.models.user.User.get')
@patch('flask_jwt_extended.get_jwt_identity')
def test_get_user_found(mock_jwt_identity, mock_get, client):
    mock_jwt_identity.return_value = 'user123'
    mock_get.return_value = {'user_id': '1', 'username': 'testuser'}
    user_id = 'user123'
    access_token = create_access_token(identity=user_id)
    headers = {
        'Authorization': f'Bearer {access_token}'
    }

    response = client.get('/users/1', headers=headers)
    assert response.status_code == 200
    assert 'testuser' in response.get_json()['username']

@patch('app.models.user.User.get')
@patch('flask_jwt_extended.get_jwt_identity')
def test_get_user_not_found(mock_jwt_identity, mock_get, client):
    mock_jwt_identity.return_value = 'user123'
    mock_get.return_value = None
    user_id = 'user123'
    access_token = create_access_token(identity=user_id)
    headers = {
        'Authorization': f'Bearer {access_token}'
    }

    response = client.get('/users/1', headers=headers)
    assert response.status_code == 404
    assert 'User not found' in response.get_json()['error']

@patch('app.models.user.User.list')
@patch('flask_jwt_extended.get_jwt_identity')
def test_list_users_success(mock_jwt_identity, mock_list, client):
    mock_jwt_identity.return_value = 'user123'
    mock_list.return_value = [{'user_id': '1', 'username': 'testuser'}, {'user_id': '2', 'username': 'anotheruser'}]
    user_id = 'user123'
    access_token = create_access_token(identity=user_id)
    headers = {
        'Authorization': f'Bearer {access_token}'
    }

    response = client.get('/users/', headers=headers)
    assert response.status_code == 200
    assert len(response.get_json()) == 2

@patch('app.models.user.User.update')
@patch('flask_jwt_extended.get_jwt_identity')
def test_update_user_success(mock_jwt_identity, mock_update, client):
    mock_jwt_identity.return_value = 'user123'
    mock_update.return_value = None
    user_id = 'user123'
    access_token = create_access_token(identity=user_id)
    headers = {
        'Authorization': f'Bearer {access_token}'
    }

    response = client.put('/users/1', json={'username': 'updateduser'}, headers=headers)
    assert response.status_code == 200
    assert 'User updated successfully' in response.get_json()['message']

@patch('app.models.user.User.delete')
@patch('flask_jwt_extended.get_jwt_identity')
def test_delete_user_success(mock_jwt_identity, mock_delete, client):
    mock_jwt_identity.return_value = 'user123'
    mock_delete.return_value = None
    user_id = 'user123'
    access_token = create_access_token(identity=user_id)
    headers = {
        'Authorization': f'Bearer {access_token}'
    }

    response = client.delete('/users/1', headers=headers)
    assert response.status_code == 200
    assert 'User deleted successfully' in response.get_json()['message']
