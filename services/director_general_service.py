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
                attachment_urls = DirectorGeneralService.get_attachment_urls(API_KEY, REDMINE_URL, issue.get("custom_fields", []))
                processed_issues.append({
                    "id": issue.get("id"),
                    "subject": issue.get("subject"),
                    "status": issue.get("status", {}).get("name"),
                    "assigned_to": issue.get("assigned_to", {}).get("name"),
                    "exploration_license_no": custom_fields.get("Exploration Licence No"),
                    "Land_Name": custom_fields.get("Land Name(Licence Details)"),
                    "Land_owner_name": custom_fields.get("Land owner name"),
                    "Name_of_village": custom_fields.get("Name of village"),
                    "Grama_Niladhari": custom_fields.get("Grama Niladhari Division"),
                    "Divisional_Secretary_Division": custom_fields.get("Divisional Secretary Division"),
                    "administrative_district": custom_fields.get("Administrative District"),
                    "Capacity": custom_fields.get("Capacity"),
                    "Mobile_Numbe": custom_fields.get("Mobile Numbe"),
                    "Google_location": custom_fields.get("Google location"), 
                    "Detailed_Plan": attachment_urls.get("Detailed Mine Restoration Plan") or custom_fields.get("Detailed Mine Restoration Plan"),     
                    "Payment_Receipt": attachment_urls.get("Payment Receipt") or custom_fields.get("Payment Receipt"),  
                    "Deed_Plan": attachment_urls.get("Deed and Survey Plan") or custom_fields.get("Deed and Survey Plan"),  
                })

            return processed_issues, None

        except Exception as e:
            return None, f"Server error: {str(e)}"
    
    @staticmethod
    def get_attachment_urls(api_key, redmine_url, custom_fields):
        try:
            # Define the mapping of custom field names to their attachment IDs
            file_fields = {
                "Detailed Mine Restoration Plan": None,
                "Deed and Survey Plan": None,
                "Payment Receipt": None     
            }

            # Extract attachment IDs from custom fields
            for field in custom_fields:
                field_name = field.get("name")
                attachment_id = field.get("value")

                if field_name in file_fields and attachment_id.isdigit():
                    file_fields[field_name] = attachment_id

            # Fetch URLs for valid attachment IDs
            file_urls = {}
            for field_name, attachment_id in file_fields.items():
                if attachment_id:
                    attachment_url = f"{redmine_url}/attachments/{attachment_id}.json"
                    response = requests.get(
                        attachment_url,
                        headers={"X-Redmine-API-Key": api_key, "Content-Type": "application/json"}
                    )

                    if response.status_code == 200:
                        attachment_data = response.json().get("attachment", {})
                        file_urls[field_name] = attachment_data.get("content_url", "")

            return file_urls

        except Exception as e:
            return {}
        

    @staticmethod
    def dg_approve_licenses(token, issue_id, update_data):
        try:
            REDMINE_URL = os.getenv("REDMINE_URL")
            API_KEY = JWTUtils.get_api_key_from_token(token)

            if not REDMINE_URL or not API_KEY:
                return None, "Redmine URL or API Key is missing"

            status_id = update_data.get("status_id")
            payload = {
                "issue": {
                    "status_id": status_id,
                }
            }

            headers = {
                "Content-Type": "application/json",
                "X-Redmine-API-Key": API_KEY
            }

            response = requests.put(
                f"{REDMINE_URL}/issues/{issue_id}.json",
                json=payload,
                headers=headers
            )

            # Handle 204 No Content as a success case
            if response.status_code == 200:
                return response.json(), None
            elif response.status_code == 204:
                return {"message": "Issue updated successfully, but no content returned."}, None
            else:
                error_msg = f"Redmine API error: {response.status_code}"
                if response.text:
                    error_msg += f" - {response.text[:200]}"
                return None, error_msg

        except requests.exceptions.RequestException as e:
            return None, f"Request failed: {str(e)}"
        except Exception as e:
            return None, f"Unexpected error: {str(e)}"

