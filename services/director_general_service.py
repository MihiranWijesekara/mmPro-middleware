import os
from dotenv import load_dotenv
import requests
from utils.MLOUtils import MLOUtils
from utils.jwt_utils import JWTUtils
from utils.limit_utils import LimitUtils


load_dotenv()

class DirectorGeneralService:

    ORS_API_KEY = os.getenv("ORS_API_KEY")

    @staticmethod
    def get_dg_pending_licenses(token):
        try:
            REDMINE_URL = os.getenv("REDMINE_URL")
            API_KEY = JWTUtils.get_api_key_from_token(token)

            if not REDMINE_URL or not API_KEY:
                return None, "Redmine URL or API Key is missing"

            # Step 1: Extract user_id from the token
            user_id, error = MLOUtils.get_user_info_from_token(token)
            if not user_id:
                return None, error

            # Step 2: Define query parameters for project_id=1 and tracker_id=4 (ML)
            params = {
                "project_id": 1,
                "tracker_id": 4,  # ML tracker ID
                "status_id": 35 
            }

            headers = {
                "X-Redmine-API-Key": API_KEY
            }

            # Make the Redmine request
            limit = LimitUtils.get_limit()
            response = requests.get(
                f"{REDMINE_URL}/projects/mmpro-gsmb/issues.json?offset=0&limit={limit}",
                params=params,
                headers=headers
            )

            # Check if the request was successful
            if response.status_code != 200:
                error_msg = f"Redmine API error: {response.status_code}"
                if response.text:
                    error_msg += f" - {response.text[:200]}"  # Truncate long error messages
                return None, error_msg

            data = response.json()
            issues = data.get("issues", [])

            processed_issues = []
            for issue in issues:
                custom_fields = {field['name']: field['value'] 
                           for field in issue.get('custom_fields', []) 
                           if field.get('value') and str(field.get('value')).strip()}
                processed_issues.append({
                    "id": issue.get("id"),
                    "subject": issue.get("subject"),
                    "status": issue.get("status", {}).get("name"),
                    "assigned_to": issue.get("assigned_to", {}).get("name"),
                    "exploration_license_no": custom_fields.get("Exploration Licence No"),
     
                    
                })

            return processed_issues, None

        except Exception as e:
            return None, f"Server error: {str(e)}"
