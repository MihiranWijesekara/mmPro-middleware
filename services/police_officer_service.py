import os
import requests
from dotenv import load_dotenv
from utils.jwt_utils import JWTUtils
from utils.user_utils import UserUtils

load_dotenv()

class PoliceOfficerService:
    @staticmethod
    def check_lorry_number(lorry_number,token):
        try:
            REDMINE_URL = os.getenv("REDMINE_URL")

            API_KEY = JWTUtils.get_api_key_from_token(token)

            if not REDMINE_URL or not API_KEY:
                return None, "Redmine URL or API Key is missing"

            headers = {"X-Redmine-API-Key": API_KEY}

            tpl_params = {"tracker_id": 8}
            tpl_response = requests.get(f"{REDMINE_URL}/issues.json", params=tpl_params, headers=headers)

            if tpl_response.status_code != 200:
                return None, f"Failed to fetch TPL issues: {tpl_response.status_code} - {tpl_response.text}"

            tpl_issues = tpl_response.json().get("issues", [])

            lorry_number_lower = lorry_number.lower()

            tpl_license = next((issue for issue in tpl_issues if any(
                cf["id"] == 13 and cf["value"].lower() == lorry_number_lower for cf in issue.get("custom_fields", [])
            )), None)

            if not tpl_license:
                return None, "No TPL with this lorry number"

            tpl_data = {
                "loadNumber": tpl_license["id"],  # Load number
                "capacity": next((cf["value"] for cf in tpl_license["custom_fields"] if cf["id"] == 15), None),
                "destination": next((cf["value"] for cf in tpl_license["custom_fields"] if cf["id"] == 12), None),
                "start": tpl_license.get("start_date"),
                "dueDate": tpl_license.get("due_date")
            }

            # Fetch all Mining Licenses (tracker_id = 7)
            ml_params = {"tracker_id": 7}
            ml_response = requests.get(f"{REDMINE_URL}/issues.json", params=ml_params, headers=headers)

            if ml_response.status_code != 200:
                return None, f"Failed to fetch Mining License issues: {ml_response.status_code} - {ml_response.text}"

            ml_issues = ml_response.json().get("issues", [])

           # Find the corresponding Mining License based on the license number
            mining_license = next((issue for issue in ml_issues if issue["subject"] == next(
            (cf["value"] for cf in tpl_license.get("custom_fields", []) if cf["id"] == 8), None)), None)

            if not mining_license:
                return None, "No matching Mining License found"

            # Extract required Mining License details
            mining_data = {
                "licenseNumber": mining_license["subject"],
                "expires": mining_license.get("due_date"),
                "owner": next((cf["value"] for cf in mining_license["custom_fields"] if cf["id"] == 2), None),
                "location": next((cf["value"] for cf in mining_license["custom_fields"] if cf["id"] == 11), None),
            }

            # Combine results
            result = {**tpl_data, **mining_data}

            return result, None

        except Exception as e:
            return None, f"Server error: {str(e)}"

    @staticmethod
    def create_complaint(vehicleNumber, userID, token):

        REDMINE_URL = os.getenv("REDMINE_URL")
        phoneNumber = UserUtils.get_user_phone(userID)
        print(phoneNumber)

        issue_data = {
                'issue': {
                    'project_id': 31,  
                    'tracker_id': 26,  
                    'subject': "New Complaint",  
                    'status_id': 11, 
                    'priority_id': 2,  
                    'assigned_to_id': 59,
                    'custom_fields': [
                        {'id': 3, 'name': "Mobile Number", 'value': phoneNumber},
                        {'id': 13, 'name': "Lorry Number", 'value': vehicleNumber},
                        {'id': 68, 'name': "Role", 'value': "PoliceOfficer"}
                    ]
                }
            }

        api_key = JWTUtils.get_api_key_from_token(token)

        response = requests.post(
            f'{REDMINE_URL}/issues.json',
            json=issue_data,
            headers={'X-Redmine-API-Key': api_key, 'Content-Type': 'application/json'}
        )

        if response.status_code == 201:
            issue_id = response.json()['issue']['id']
            return True, issue_id
        else:
            return False, 'Failed to create complaint'