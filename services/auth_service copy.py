import requests
from dotenv import load_dotenv
import os
from google.auth.transport import requests as google_requests
from google.oauth2 import id_token
from config import Config
import datetime
import jwt


load_dotenv()

GOOGLE_CLIENT_ID = os.getenv("GOOGLE_CLIENT_ID")
REDMINE_URL = os.getenv("REDMINE_URL")
REDMINE_ADMIN_API_KEY = os.getenv("REDMINE_ADMIN_API_KEY")
            
class AuthService:
    @staticmethod
    def authenticate_user(username, password):
        try:
            # Authenticate user and get current user info
            response = requests.get(
                f"{REDMINE_URL}/users/current.json?include=memberships,groups",
                auth=(username, password)
            )

            if response.status_code != 200:
                return None, None, 'Invalid credentials'

            user_data = response.json().get('user')
            if not user_data:
                return None, None, 'User data not found'

            # Check for the GSMB project role
            gsm_project_role = None
            for membership in user_data.get('memberships', []):
                project_name = membership.get('project', {}).get('name')
                if project_name == "GSMB":
                    roles = membership.get('roles', [])
                    if roles:
                        gsm_project_role = roles[0].get('name')
                        break

            if not gsm_project_role:
                return None, None, 'User does not have a role in project GSMB'

            # Extract the API key (Redmine exposes it under 'api_key')
            api_key = user_data.get('api_key')
            if not api_key:
                return user_data, gsm_project_role, 'API key not found'

            return user_data, gsm_project_role, api_key

        except Exception as e:
            return None, None, f"Server error: {str(e)}"
        
    @staticmethod
    def authenticate_google_token(token):
        try:
            # Verify the Google token using Google's OAuth2 service
            id_info = id_token.verify_oauth2_token(
                token,
                google_requests.Request(),
                GOOGLE_CLIENT_ID
            )

            # Extract email from the token info
            email = id_info.get('email')
            if not email:
                return None, "Email not found in Google token"

            # Get User ID from Redmine
            users_response = requests.get(
                f"{REDMINE_URL}/users.json",
                params={"mail": email},
                headers={"X-Redmine-API-Key": REDMINE_ADMIN_API_KEY}
            )

            if users_response.status_code != 200 or not users_response.json().get('users'):
                return None, "User not found in Redmine"

            user_id = users_response.json()['users'][0]['id']

            # Get User Role from Redmine Memberships
            memberships_response = requests.get(
                f"{REDMINE_URL}/projects/GSMB/memberships.json",
                headers={"X-Redmine-API-Key": REDMINE_ADMIN_API_KEY}
            )

            if memberships_response.status_code != 200:
                return None, "Failed to fetch Redmine memberships"

            memberships = memberships_response.json().get('memberships', [])

            # Find the role associated with the user_id
            user_role = None
            for membership in memberships:
                if membership.get('user', {}).get('id') == user_id:
                    user_role = membership.get('roles', [{}])[0].get('name')  # Assuming first role is primary

            if not user_role:
                return None, "User role not found in Redmine"

            return {"email": email, "role": user_role}, None

        except ValueError as e:
            return None, f"Invalid Google token: {str(e)}"
        except Exception as e:
            return None, f"Server error: {str(e)}"    


    @staticmethod
    def create_jwt_token(role):
        """Utility function to create a JWT token."""
        expiration_time = datetime.datetime.now(datetime.timezone.utc) + datetime.timedelta(hours=1)
        jwt_token = jwt.encode(
            {'role': role,'exp': expiration_time},
            Config.SECRET_KEY,
            algorithm=Config.JWT_ALGORITHM
        )
        return jwt_token