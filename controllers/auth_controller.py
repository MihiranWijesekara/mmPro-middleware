from flask import Blueprint, request, jsonify
from services.auth_service import AuthService

auth_bp = Blueprint('auth_controller', __name__)

# CORS(app)

@auth_bp.route('/login', methods=['POST'])
def login():
    data = request.get_json()
    username = data.get('username')
    password = data.get('password')

    if not username or not password:
        return jsonify({'message': 'Username and password are required'}), 400

    user_data, user_role = AuthService.authenticate_user(username, password)
    
    if not user_data:
        return jsonify({'message': user_role}), 401

    # Create JWT token using the service
    jwt_token = AuthService.create_jwt_token(user_role)

    return jsonify({'token': jwt_token, 'role': user_role})


@auth_bp.route('/google-login', methods=['POST'])
def auth_google():
    token = request.json.get('token')
    if not token:
        return jsonify({"error": "Google token is required"}), 400
    
    user_data, error = AuthService.authenticate_google_token(token)
    if error:
        return jsonify({"error": error}), 400

    # Create JWT token using the service
    jwt_token = AuthService.create_jwt_token(user_data['role'])

    return jsonify({'token': jwt_token, 'role': user_data['role']}), 200
