from flask import request, jsonify, render_template, redirect, url_for, session
from . import auth_bp
from app.models.user import User
from flask_jwt_extended import create_access_token, jwt_required, get_jwt_identity
import uuid
import json

@auth_bp.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'GET':
        return render_template('register.html')
    
    data = request.form.to_dict()
    user_id = str(uuid.uuid4())
    contact_info = {
        'email': data.get('email'),
        'phone': data.get('phone')
    }
    
    if any([x not in data for x in ['username', 'password']]) or any([not x for x in [data['username'], data['password'], contact_info['email'], contact_info['phone']]]):
        return jsonify({'error': 'Invalid request. Please enter all the required params'}), 400
    
    user = {
        'UserID': user_id,
        'Username': data['username'],
        'HashedPassword': data['password'],
        'ContactInfo': contact_info,
        'OrganizedEvents': []
    }
    
    if User.get_by_username(data['username']):
        return jsonify({'error': 'Username already exists'}), 400
    
    User.create(user)
    return redirect(url_for('auth_bp.login'))

@auth_bp.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'GET':
        return render_template('login.html')
    print(json.dumps(request.form.to_dict()))
    data = request.form.to_dict()
    
    if any([x not in data for x in ['username', 'password']]) or any([not x for x in [data['username'], data['password']]]):
        return jsonify({'error': 'Invalid request. Please enter all the required params'}), 400
    
    user = User.get_by_username(data['username'])
    if user and User.check_password(user['HashedPassword'], data['password']):
        access_token = create_access_token(identity=user['UserID'])
        session['auth_token'] = access_token
        return render_template('dashboard.html')
    
    return jsonify({'error': 'Invalid username or password'}), 401

@auth_bp.route('/logout')
def logout():
    session.pop('auth_token', None)
    session.pop('user_id', None) 
    return redirect(url_for('auth_bp.login'))

@auth_bp.route('/dashboard', methods=['GET'])
@jwt_required()
def dashboard():
    return render_template('dashboard.html')

@auth_bp.before_request
def check_token():
    # This will run before each request to this blueprint
    if 'auth_token' not in session and request.endpoint not in ['auth_bp.login', 'auth_bp.register']:
        return redirect(url_for('auth_bp.login'))
