from flask import request, jsonify
from . import auth_bp
from app.models.user import User
from flask_jwt_extended import create_access_token
import uuid

@auth_bp.route('/register', methods=['POST'])
def register():
    user_id = str(uuid.uuid4())
    data = request.get_json()
    if any([x not in data for x in ['username', 'password', 'contactInfo']]) or any([x not in data['contactInfo'] for x in ['email', 'phone']]) or any([not x for x in [data['username'], data['password'], data['contactInfo']['phone'], data['contactInfo']['email']]]):
        return jsonify({'error': 'Invalid request. Please enter all the required params'}), 400
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
def login():
    data = request.get_json()
    if any([x not in data for x in ['username', 'password']]) or any([not x for x in [data['username'], data['password']]]):
        return jsonify({'error': 'Invalid request. Please enter all the required params'}), 400
    user = User.get_by_username(data['username'])
    if user and User.check_password(user['HashedPassword'], data['password']):
        access_token = create_access_token(identity=user['UserID'])
        return jsonify(access_token=access_token), 200
    return jsonify({'error': 'Invalid username or password'}), 401
