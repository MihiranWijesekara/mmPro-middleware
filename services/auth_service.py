import requests
from dotenv import load_dotenv
import os
from google.auth.transport import requests as google_requests
from google.oauth2 import id_token
from config import Config
from cryptography.fernet import Fernet

load_dotenv()

GOOGLE_CLIENT_ID = os.getenv("GOOGLE_CLIENT_ID")
REDMINE_URL = os.getenv("REDMINE_URL")
REDMINE_ADMIN_API_KEY = os.getenv("REDMINE_ADMIN_API_KEY")
class AuthService:
    ENCRYPTION_KEY = Fernet.generate_key()  # Generate only once and store safely
    cipher = Fernet(ENCRYPTION_KEY)
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

            gsm_project_role = None
            for membership in user_data.get('memberships', []):
                project_name = membership.get('project', {}).get('name')
                print(f"Checking project: {project_name}")
                if project_name == "GSMB":
                    roles = membership.get('roles', [])
                    if roles:
                        gsm_project_role = roles[0].get('name')
                        break

            if not gsm_project_role:
                return None, None, 'User does not have a role in project GSMB'

            api_key = user_data.get('api_key')
            if not api_key:
                return None, None, 'API key not found'

            return user_data, gsm_project_role, api_key

        except Exception as e:
            return None, None, f"Server error: {str(e)}"

    @staticmethod
    def authenticate_google_token(token):
        try:
            # Verify the Google token using Google's OAuth2 service
            print(token)
            id_info = id_token.verify_oauth2_token(
                token,
                google_requests.Request(),
                GOOGLE_CLIENT_ID
            )


            # Extract email from the token info
            email = id_info.get('email')
            print(email)
            print(f'the email is {email}')
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
            user_data = users_response.json()['users'][0] 

            user_details_response = requests.get(
                f"{REDMINE_URL}/users/{user_id}.json",
                headers={"X-Redmine-API-Key": REDMINE_ADMIN_API_KEY}
            )

            if user_details_response.status_code != 200:
                return None, "Failed to fetch user details"

            # Extract API key from the user details response
            user_details = user_details_response.json().get('user', {})
            api_key = user_details.get('api_key')
            if not api_key:
                return None, "API key not found for the user"

            # Get User Role from Redmine Memberships
            memberships_response = requests.get(
                f"{REDMINE_URL}/projects/GSMB/memberships.json",
                headers={"X-Redmine-API-Key": REDMINE_ADMIN_API_KEY}
            )

            if memberships_response.status_code != 200:
                return None, "Failed to fetch Redmine memberships"

            memberships = memberships_response.json().get('memberships', [])

            # Find the role associated with the user_id
            gsm_project_role = None
            for membership in memberships:
                if membership.get('user', {}).get('id') == user_id:
                    gsm_project_role = membership.get('roles', [{}])[0].get('name')  # Assuming first role is primary

            if not gsm_project_role:
                return None, "User role not found in Redmine"

            return user_id,user_data,gsm_project_role,api_key

        except ValueError as e:
            return None, f"Invalid Google token: {str(e)}"
        except Exception as e:
            return None, f"Server error: {str(e)}"
        
    @staticmethod
    def authenticate_google_access_token(access_token):
        try:
            # Here, we use Google's access token verification
            response = requests.get(
                f"https://www.googleapis.com/oauth2/v1/tokeninfo?access_token={access_token}"
            )
            
            if response.status_code != 200:
                return None, "Failed to verify access token with Google"

            id_info = response.json()

            # Extract email and other user information from the access token
            email = id_info.get('email')
            if not email:
                return None, "Email not found in access token"

            # Proceed with the same logic for fetching user info from Redmine
            users_response = requests.get(
                f"{REDMINE_URL}/users.json",
                params={"mail": email},
                headers={"X-Redmine-API-Key": REDMINE_ADMIN_API_KEY}
            )

            if users_response.status_code != 200 or not users_response.json().get('users'):
                return None, "User not found in Redmine"

            user_id = users_response.json()['users'][0]['id']
            user_data = users_response.json()['users'][0]

            user_details_response = requests.get(
                f"{REDMINE_URL}/users/{user_id}.json",
                headers={"X-Redmine-API-Key": REDMINE_ADMIN_API_KEY}
            )

            if user_details_response.status_code != 200:
                return None, "Failed to fetch user details"

            user_details = user_details_response.json().get('user', {})
            api_key = user_details.get('api_key')
            if not api_key:
                return None, "API key not found for the user"

            memberships_response = requests.get(
                f"{REDMINE_URL}/projects/GSMB/memberships.json",
                headers={"X-Redmine-API-Key": REDMINE_ADMIN_API_KEY}
            )

            if memberships_response.status_code != 200:
                return None, "Failed to fetch Redmine memberships"

            memberships = memberships_response.json().get('memberships', [])

            gsm_project_role = None
            for membership in memberships:
                if membership.get('user', {}).get('id') == user_id:
                    gsm_project_role = membership.get('roles', [{}])[0].get('name')

            if not gsm_project_role:
                return None, "User role not found in Redmine"

            return user_id, user_data, gsm_project_role, api_key

        except Exception as e:
            return None, f"Error: {str(e)}"


    # @staticmethod
    # def create_jwt_token(user_id,user_role, api_key):
    #     """Utility function to create a JWT token."""
    #     encrypted_api_key = AuthService.cipher.encrypt(api_key.encode()).decode()
    #     expiration_time = datetime.datetime.now(datetime.timezone.utc) + datetime.timedelta(hours=1)
    #     jwt_token = jwt.encode(
    #         {'role': user_role, 'user_id':user_id,'api_key':encrypted_api_key, 'exp': expiration_time},
    #         Config.SECRET_KEY,
    #         algorithm=Config.JWT_ALGORITHM
    #     )
    #     return jwt_token

    # @staticmethod
    # def decrypt_api_key(encrypted_api_key):
    #     """Decrypt the API key."""
    #     return AuthService.cipher.decrypt(encrypted_api_key.encode()).decode()
