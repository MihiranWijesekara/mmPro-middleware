import os
import requests
from dotenv import load_dotenv
from twilio.rest import Client
from twilio.base.exceptions import TwilioException


load_dotenv()

TWILIO_ACCOUNT_SID = 'ACa759a9d29d1d24aa02d64738deb44648'
TWILIO_AUTH_TOKEN = '4cb3b1b8d96018cecca30311ec93b70d'  # Replace with your actual auth token
VERIFY_SERVICE_SID = 'VAf1d2907542dd6d49d431e876a521f2fc'

client = Client(TWILIO_ACCOUNT_SID, TWILIO_AUTH_TOKEN)

REDMINE_URL = os.getenv("REDMINE_URL")
API_KEY = os.getenv("REDMINE_ADMIN_API_KEY")

class GeneralPublicService:
    @staticmethod
    def is_lorry_number_valid(lorry_number):
        try:

            if not REDMINE_URL or not API_KEY:
                return None, "Redmine URL or API Key is missing"

            headers = {"X-Redmine-API-Key": API_KEY}

            # Fetch all TPL licenses (tracker_id = 8)
            tpl_params = {"tracker_id": 8}
            tpl_response = requests.get(f"{REDMINE_URL}/issues.json", params=tpl_params, headers=headers)

            if tpl_response.status_code != 200:
                return None, f"Failed to fetch TPL issues: {tpl_response.status_code} - {tpl_response.text}"

            tpl_issues = tpl_response.json().get("issues", [])

            lorry_number_lower = lorry_number.lower()

            # Check if any TPL license matches the given lorry number (cf_13)
            tpl_license_exists = any(
                any(cf["id"] == 13 and cf["value"].lower() == lorry_number_lower for cf in issue.get("custom_fields", []))
                for issue in tpl_issues
            )

            return tpl_license_exists, None  # Return True if exists, False if not

        except Exception as e:
            return None, f"Server error: {str(e)}"
        
    @staticmethod
    def send_verification_code(phone):
        try:
            verification = client.verify \
                .v2 \
                .services(VERIFY_SERVICE_SID) \
                .verifications \
                .create(to=phone, channel='sms')

            return True, verification.sid
        except TwilioException as e:
            return False, str(e)

    @staticmethod
    def verify_code(phone, code):
        try:
            verification_check = client.verify \
                .v2 \
                .services(VERIFY_SERVICE_SID) \
                .verification_checks \
                .create(to=phone, code=code)

            if verification_check.status == 'approved':
                return True, None
            else:
                return False, 'Invalid code'
        except TwilioException as e:
            return False, str(e)

    @staticmethod
    def create_complaint(phone):
        issue_data = {
            'issue': {
                'project_id': 31,
                'tracker_id': 26,
                'subject': "New Complaint",
                'status_id': 11,
                'priority_id': 2,
                'assigned_to_id': 59,
                'start_date': "2024-01-31",
                'due_date': "2024-02-14",
                'custom_fields': [
                    {'id': 3, 'name': "Mobile Number", 'value': phone},
                    {'id': 90, 'name': "Complaint ID", 'value': "complaint01"}
                ]
            }
        }

        response = requests.post(
            f'{REDMINE_URL}/issues.json',
            json=issue_data,
            headers={'X-Redmine-API-Key': API_KEY, 'Content-Type': 'application/json'}
        )

        if response.status_code == 201:
            issue_id = response.json()['issue']['id']
            return True, issue_id
        else:
            return False, 'Failed to create complaint'