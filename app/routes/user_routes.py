from flask import request, jsonify
from flask_jwt_extended import jwt_required
from . import user_bp
from app.models.user import User

@user_bp.route('/<user_id>', methods=['GET'])
@jwt_required()
def get_user(user_id):
    user = User.get(user_id)
    if user:
        return jsonify(user)
    else:
        return jsonify({'error': 'User not found'}), 404

@user_bp.route('/', methods=['GET'])
@jwt_required()
def list_users():
    users = User.list()
    return jsonify(users)

@user_bp.route('/<user_id>', methods=['PUT'])
@jwt_required()
def update_user(user_id):
    data = request.get_json()
    User.update(user_id, data)
    return jsonify({'message': 'User updated successfully'})

@user_bp.route('/<user_id>', methods=['DELETE'])
@jwt_required()
def delete_user(user_id):
    User.delete(user_id)
    return jsonify({'message': 'User deleted successfully'})
