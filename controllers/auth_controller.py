from flask import Blueprint, request, jsonify
from services.auth_service import AuthService
from utils.jwt_utils import JWTUtils
from utils.user_utils import UserUtils
import jwt
from config import Config
import requests

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

# testing code delete
@auth_bp.route('/tracker-issues', methods=['GET'])
def get_tracker_issues():
    """
    Get Sample Tracker Issues Endpoint
    - Fetches issues from Redmine API with tracker_id=9
    - Acts as a proxy to avoid CORS issues
    - Returns the issues data
    """
    # Your Redmine API configuration
    REDMINE_API_URL = "http://gsmb.aasait.lk/issues.json"
    REDMINE_API_KEY = "2fe97b781bc33e9d38305356949639971a921fb0"  # Move this to config in production
    
    # Required parameters
    project_id = request.args.get('project_id', default=1, type=int)
    tracker_id = request.args.get('tracker_id', default=9, type=int)
    
    try:
        # Make request to Redmine API
        response = requests.get(
            REDMINE_API_URL,
            params={
                'project_id': project_id,
                'tracker_id': tracker_id,
                'include': 'attachments'
            },
            headers={
                'X-Redmine-API-Key': REDMINE_API_KEY,
                'Content-Type': 'application/json'
            }
        )
        
        # Check for errors
        response.raise_for_status()
        
        # Return the data to the frontend
        return jsonify(response.json()), 200
        
    except requests.exceptions.RequestException as e:
        # Handle different types of errors
        error_message = str(e)
        status_code = 500
        
        if isinstance(e, requests.exceptions.HTTPError):
            status_code = e.response.status_code
            try:
                error_details = e.response.json()
                error_message = error_details.get('error', error_message)
            except ValueError:
                error_message = e.response.text or error_message
        
        return jsonify({
            'error': 'Failed to fetch tracker issues',
            'details': error_message
        }), status_code

@auth_bp.route('/create-issue', methods=['POST'])
def create_issue():
    """
    Create New Issue Endpoint
    - Creates a new issue in Redmine with attachments
    - Properly handles file uploads to Redmine
    """
    REDMINE_API_URL = "http://gsmb.aasait.lk/issues.json"
    REDMINE_UPLOAD_URL = "http://gsmb.aasait.lk/uploads.json"
    REDMINE_API_KEY = "2fe97b781bc33e9d38305356949639971a921fb0"

    try:
        # Validate input
        if 'file' not in request.files:
            return jsonify({'error': 'No file provided'}), 400
            
        file = request.files['file']
        if file.filename == '':
            return jsonify({'error': 'No selected file'}), 400

        start_date = request.form.get('start_date')
        due_date = request.form.get('due_date')
        
        if not all([start_date, due_date]):
            return jsonify({'error': 'Missing required fields'}), 400

        # Step 1: Upload the file first to get token
        upload_response = requests.post(
            REDMINE_UPLOAD_URL,
            headers={
                'X-Redmine-API-Key': REDMINE_API_KEY,
                'Content-Type': 'application/octet-stream',
                'Accept': 'application/json'  # Explicitly accept JSON responses
            },
            data=file.stream  # Send the file as binary
        )
        
        if upload_response.status_code != 201:
            return jsonify({
                'error': 'File upload failed',
                'details': upload_response.text
            }), upload_response.status_code

        upload_token = upload_response.json().get('upload', {}).get('token')
        if not upload_token:
            return jsonify({'error': 'Failed to get upload token'}), 500

        # Step 2: Create the issue with the upload token
        issue_data = {
            "issue": {
                "project_id": 1,
                "tracker_id": 9,
                "subject": f"New issue",
                "start_date": start_date,
                "due_date": due_date,
                "description": "Issue created via API",
                "uploads": [{
                    "token": upload_token,
                    "filename": file.filename,
                    "content_type": file.content_type,
                    "description":"survey report"
                }]
            }
        }

        response = requests.post(
            REDMINE_API_URL,
            headers={
                'X-Redmine-API-Key': REDMINE_API_KEY,
                'Content-Type': 'application/json'
            },
            json=issue_data
        )

        if response.status_code != 201:
            return jsonify({
                'error': 'Issue creation failed',
                'details': response.text
            }), response.status_code

        issue_id = response.json().get('issue', {}).get('id')
        return jsonify({
            'message': 'Issue created successfully',
            'issue_id': issue_id
        }), 201

    except Exception as e:
        return jsonify({
            'error': 'Internal server error',
            'details': str(e)
        }), 500