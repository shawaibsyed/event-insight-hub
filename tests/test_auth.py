import pytest
from flask import json
from unittest.mock import patch
from run import app
import re

@pytest.fixture
def client():
    with app.test_client() as client:
        yield client

@patch('app.models.user.User.get_by_username')
@patch('app.models.user.User.create')
def test_register_new_user(mock_create, mock_get_by_username, client):
    mock_get_by_username.return_value = None
    response = client.post('/auth/register', json={
        'username': 'newuser',
        'password': 'password123',
        'contactInfo': {'phone': '1234567890', 'email': 'test@example.com'}
    })
    assert response.status_code == 201
    assert 'User registered successfully' in response.get_json()['message']
    mock_create.assert_called_once()

@patch('app.models.user.User.get_by_username')
def test_register_existing_user(mock_get_by_username, client):
    mock_get_by_username.return_value = True
    response = client.post('/auth/register', json={
        'username': 'existinguser',
        'password': 'password123',
        'contactInfo': {'phone': '1234567890', 'email': 'test@example.com'}
    })
    assert response.status_code == 400
    assert 'Username already exists' in response.get_json()['error']


@patch('app.models.user.User.get_by_username')
@patch('app.models.user.User.check_password')
@patch('flask_jwt_extended.create_access_token')
def test_login_successful(mock_create_access_token, mock_check_password, mock_get_by_username, client):
    mock_get_by_username.return_value = {'UserID': '1', 'HashedPassword': 'hashedpassword'}
    mock_check_password.return_value = True
    mock_create_access_token.return_value = 'generated_token'
    response = client.post('/auth/login', json={
        'username': 'validuser',
        'password': 'correctpassword'
    })
    assert response.status_code == 200
    assert 'access_token' in response.get_json()
    token = response.get_json()['access_token']
    # Optionally check the format of the token
    assert re.match(r'^[A-Za-z0-9\-_]+\.[A-Za-z0-9\-_]+\.[A-Za-z0-9\-_]+$', token)



@patch('app.models.user.User.get_by_username')
def test_login_invalid_username(mock_get_by_username, client):
    mock_get_by_username.return_value = None
    response = client.post('/auth/login', json={
        'username': 'nonexistentuser',
        'password': 'password123'
    })
    assert response.status_code == 401
    assert 'Invalid username or password' in response.get_json()['error']

@patch('app.models.user.User.get_by_username')
@patch('app.models.user.User.check_password')
def test_login_invalid_password(mock_check_password, mock_get_by_username, client):
    mock_get_by_username.return_value = {'UserID': '1', 'HashedPassword': 'hashedpassword'}
    mock_check_password.return_value = False
    response = client.post('/auth/login', json={
        'username': 'validuser',
        'password': 'wrongpassword'
    })
    assert response.status_code == 401
    assert 'Invalid username or password' in response.get_json()['error']