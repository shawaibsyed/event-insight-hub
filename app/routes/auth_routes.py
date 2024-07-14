from flask import request, jsonify
from . import auth_bp
from app.models.user import User
from flask_jwt_extended import create_access_token
import uuid
from flask_request_validator import (
    Param,
    ValidRequest,
    validate_params,
    JSON
)

@auth_bp.route('/register', methods=['POST'])
@validate_params(
    Param('username', JSON, str, required=True),
    Param('password', JSON, str, required=True),
    Param('contactInfo.phone', JSON, str, required=True),
    Param('contactInfo.email', JSON, str, required=True),
)
def register(valid: ValidRequest):
    user_id = str(uuid.uuid4())
    data = valid.get_json()
    user = {
        'UserID': user_id,
        'Username': data['username'],
        'HashedPassword': data['password'],
        'ContactInfo': data['contactInfo'],
        'OrganizedEvents': []
    }
    if User.get_by_username(data['username']):
        return jsonify({'error': 'Username already exists'}), 400
    User.create(user)
    return jsonify({'message': 'User registered successfully'}), 201

@auth_bp.route('/login', methods=['POST'])
@validate_params(
    Param('username', JSON, str, required=True),
    Param('password', JSON, str, required=True),
)
def login(valid: ValidRequest):
    data = valid.get_json()
    user = User.get_by_username(data['username'])
    if user and User.check_password(user['HashedPassword'], data['password']):
        access_token = create_access_token(identity=user['UserID'])
        return jsonify(access_token=access_token), 200
    return jsonify({'error': 'Invalid username or password'}), 401
