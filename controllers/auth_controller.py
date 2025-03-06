from flask import Blueprint, request, jsonify
from services.auth_service import AuthService
from utils.jwt_utils import JWTUtils

auth_bp = Blueprint('auth_controller', __name__)

# @auth_bp.route('/login', methods=['POST'])
# def login():
#     data = request.get_json()
#     username = data.get('username')
#     password = data.get('password')

#     if not username or not password:
#         return jsonify({'message': 'Username and password are required'}), 400

#     user_data, user_role, api_key = AuthService.authenticate_user(username, password)
    
#     if not user_data:
#         return jsonify({'message': user_role}), 401

#     # Create a User object
    
#     user_id=user_data.get('id'),
#     username=f"{user_data.get('firstname')} {user_data.get('lastname')}",

#     # Create JWT token using the User's role, api_key, and user_id
#     jwt_token =  JWTUtils.create_jwt_token(user_id,user_role, api_key)

#     return jsonify({'token': jwt_token, 'role': user_role, 'username':username,'userId':user_id})

@auth_bp.route('/login', methods=['POST'])
def login():
    data = request.get_json()
    username = data.get('username')
    password = data.get('password')

    if not username or not password:
        return jsonify({'message': 'Username and password are required'}), 400

    user_data, user_role, api_key = AuthService.authenticate_user(username, password)
    
    if not user_data:
        return jsonify({'message': user_role}), 401

    # Extract user details
    user_id = user_data.get('id')
    username = f"{user_data.get('firstname')} {user_data.get('lastname')}"

    # Generate access & refresh tokens
    tokens = JWTUtils.create_jwt_token(user_id, user_role, api_key)

    return jsonify({
        'access_token': tokens['access_token'],
        'refresh_token': tokens['refresh_token'],
        'role': user_role,
        'username': username,
        'userId': user_id
    })


@auth_bp.route('/google-login', methods=['POST'])
def auth_google():
    token = request.json.get('token')
    if not token:
        return jsonify({"error": "Google token is required"}), 400
    
    auth_result = AuthService.authenticate_google_token(token)
    
    if auth_result[0] is None:  # If authentication failed
        return jsonify({"error": auth_result[1]}), 401

    user_id, user_data, user_role, api_key = auth_result  

    username=f"{user_data.get('firstname')} {user_data.get('lastname')}",
    # Create JWT token using the service
    jwt_token =  JWTUtils.create_jwt_token(user_id,user_role, api_key)

    return jsonify({'token': jwt_token, 'role': user_role, 'username':username, 'userId':user_id})

@auth_bp.route('/mobile-google-login', methods=['POST'])
def mobile_auth_google():
    access_token = request.json.get('token')
    if not access_token:
        return jsonify({"error": "Google access token is required"}), 400

    auth_result = AuthService.authenticate_google_access_token(access_token)

    if auth_result[0] is None:
        return jsonify({"error": auth_result[1]}), 401

    user_id, user_data, user_role, api_key = auth_result

    username = f"{user_data.get('firstname')} {user_data.get('lastname')}"
    jwt_token = JWTUtils.create_jwt_token(user_id, user_role, api_key)

    return jsonify({'token': jwt_token, 'role': user_role, 'username': username, 'userId': user_id})

