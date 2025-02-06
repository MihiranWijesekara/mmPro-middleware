import requests
from dotenv import load_dotenv
import os

load_dotenv()

class AuthService:
    @staticmethod
    def authenticate_user(username, password):
        try:
            REDMINE_URL = os.getenv("REDMINE_URL")
            response = requests.get(
                f"{REDMINE_URL}/users/current.json?include=memberships,groups",
                auth=(username, password)
            )

            if response.status_code != 200:
                return None, 'Invalid credentials'

            user_data = response.json().get('user')
            if not user_data:
                return None, 'User data not found'

            # Check memberships for project "GSMB"
            gsm_project_role = None
            for membership in user_data.get('memberships', []):
                project_name = membership.get('project', {}).get('name')
                if project_name == "GSMB":
                    roles = membership.get('roles', [])
                    if roles:
                        gsm_project_role = roles[0].get('name')  # Assuming the first role is what you want
                        break  # Exit loop once the GSMB project is found

            if not gsm_project_role:
                return None, 'User does not have a role in project GSMB'

            return user_data, gsm_project_role

        except Exception as e:
            return None, f"Server error: {str(e)}"
