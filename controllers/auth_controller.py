from flask import Blueprint, request, jsonify
from services.auth_service import AuthService
from utils.jwt_utils import JWTUtils
from utils.user_utils import UserUtils
import jwt
from config import Config

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
        'token': tokens['access_token'],
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


@auth_bp.route('/refresh-token', methods=['POST'])
def refresh_token():
    
    data = request.get_json()
    refresh_token = data.get("refresh_token")

    if not refresh_token:
        return jsonify({"message": "Refresh token is required"}), 401

    try:
        decoded_payload = jwt.decode(refresh_token, Config.SECRET_KEY, algorithms=[Config.JWT_ALGORITHM])

        if not decoded_payload.get("refresh"):
            return jsonify({"message": "Invalid refresh token"}), 401

        user_id = decoded_payload["user_id"]
        print(user_id)
        user_role = decoded_payload["role"]
        print(user_role)


        api_key = UserUtils.get_user_api_key(user_id)
        print(api_key)

        new_access_token = JWTUtils.create_access_token(user_id, user_role, api_key)

        return jsonify({
            'access_token': new_access_token  
        })

    except jwt.ExpiredSignatureError:
        return jsonify({"message": "Refresh token has expired"}), 401
    except jwt.InvalidTokenError:
        return jsonify({"message": "Invalid token"}), 401
    except Exception as e:
        print(f"Error processing token: {e}")  # Log error internally
        return jsonify({"message": "Internal server error"}), 500

@auth_bp.route('/forgot-password', methods=['POST'])
def forgot_password():
    """
    Forgot Password Endpoint
    - Validates the email.
    - Calls the AuthService to handle the password reset process.
    """
    data = request.get_json()
    email = data.get('email')

    if not email:
        return jsonify({'message': 'Email is required'}), 400

    # Call the AuthService to handle the password reset process
    result = AuthService.initiate_password_reset(email)

    if result.get('error'):
        return jsonify({'message': result['error']}), 400

    return jsonify({'message': 'If the email exists, a reset link will be sent'}), 200

@auth_bp.route('/reset-password', methods=['POST'])
def reset_password():
    """
    Reset Password Endpoint
    - Validates the reset token.
    - Updates the user's password.
    """
    data = request.get_json()
    token = data.get('token')
    new_password = data.get('new_password')

    if not token or not new_password:
        return jsonify({'error': 'Token and new password are required'}), 400

    # Call the AuthService to handle the password reset
    result = AuthService.reset_password(token, new_password)

    if not result.get('success'):
        error_message = result.get('error', 'Failed to reset password')
        return jsonify({'error': error_message}), 400

    return jsonify({'message': 'Password updated successfully'}), 200

