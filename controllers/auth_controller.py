import jwt
import requests
import datetime
from flask import Blueprint, request, jsonify
from config import Config
from services.auth_service import AuthService

auth_bp = Blueprint('auth', __name__)

@auth_bp.route('/login', methods=['POST'])
def login():
    data = request.get_json()
    username = data.get('username')
    password = data.get('password')

    if not username or not password:
        return jsonify({'message': 'Username and password are required'}), 400

    user_data, user_role_or_error = AuthService.authenticate_user(username, password)
    
    if not user_data:
        return jsonify({'message': user_role_or_error}), 401

    expiration_time = datetime.datetime.now(datetime.timezone.utc) + datetime.timedelta(hours=1)
    token = jwt.encode(
        {'user_id': user_data['id'], 'role': user_role_or_error, 'exp': expiration_time},
        Config.SECRET_KEY,
        algorithm=Config.JWT_ALGORITHM
    )

    return jsonify({'token': token, 'role': user_role_or_error})
