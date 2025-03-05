import os
import requests
from dotenv import load_dotenv
from twilio.rest import Client
from twilio.base.exceptions import TwilioException
from utils.jwt_utils import JWTUtils
import random
from diskcache import Cache


cache = Cache('otp_cache') 


load_dotenv()

TWILIO_ACCOUNT_SID = 'AC99293cf8d316875de7dfd3c164e90cbb'
TWILIO_AUTH_TOKEN = 'f848dae98a365e367fa4f08056c871c2'  
VERIFY_SERVICE_SID = 'VA8e0fb628c45e51612bf3e2dd68ef1efe'

client = Client(TWILIO_ACCOUNT_SID, TWILIO_AUTH_TOKEN)

REDMINE_URL = os.getenv("REDMINE_URL")
API_KEY = os.getenv("REDMINE_ADMIN_API_KEY")

class GeneralPublicService:
    # @staticmethod
    # def is_lorry_number_valid(lorry_number):
    #     try:

    #         if not REDMINE_URL or not API_KEY:
    #             return None, "Redmine URL or API Key is missing"

    #         headers = {"X-Redmine-API-Key": API_KEY}

    #         # Fetch all TPL licenses (tracker_id = 8)
    #         tpl_params = {"tracker_id": 8}
    #         tpl_response = requests.get(f"{REDMINE_URL}/issues.json", params=tpl_params, headers=headers)

    #         if tpl_response.status_code != 200:
    #             return None, f"Failed to fetch TPL issues: {tpl_response.status_code} - {tpl_response.text}"

    #         tpl_issues = tpl_response.json().get("issues", [])

    #         lorry_number_lower = lorry_number.lower()

    #         # Check if any TPL license matches the given lorry number (cf_13)
    #         tpl_license_exists = any(
    #             any(cf["id"] == 13 and cf["value"].lower() == lorry_number_lower for cf in issue.get("custom_fields", []))
    #             for issue in tpl_issues
    #         )

    #         return tpl_license_exists, None  # Return True if exists, False if not

    #     except Exception as e:
    #         return None, f"Server error: {str(e)}"

    @staticmethod
    def is_lorry_number_valid(lorry_number):
        try:
            # Extract the user-specific API key from the token
            api_key = API_KEY

            if not REDMINE_URL or not api_key:
                return None, "Redmine URL or API Key is missing"

            headers = {"X-Redmine-API-Key": api_key}

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

            return tpl_license_exists, None

        except Exception as e:
            return None, f"Server error: {str(e)}"

        
    # @staticmethod
    # def send_verification_code(phone):
    #     try:
    #         verification = client.verify \
    #             .v2 \
    #             .services(VERIFY_SERVICE_SID) \
    #             .verifications \
    #             .create(to=phone, channel='sms')

    #         return True, verification.sid
    #     except TwilioException as e:
    #         return False, str(e)

    # @staticmethod
    # def verify_code(phone, code):
    #     try:
    #         verification_check = client.verify \
    #             .v2 \
    #             .services(VERIFY_SERVICE_SID) \
    #             .verification_checks \
    #             .create(to=phone, code=code)

    #         if verification_check.status == 'approved':
    #             return True, None
    #         else:
    #             return False, 'Invalid code'
    #     except TwilioException as e:
    #         return False, str(e)

    @staticmethod
    def generate_otp():
        return str(random.randint(100000, 999999))  # Generate a 6-digit OTP

    @staticmethod
    def send_verification_code(phone):
        otp = GeneralPublicService.generate_otp()  # Generate OTP
        cache.set(phone, otp, expire=600)  # Store OTP in cache for 10 minutes

        try:
            url = "https://message.textware.lk:5001/sms/send_sms.php"
            params = {
                "username": "aasait",
                "password": "Aasait@textware123",
                "src": "TWTEST",
                "dst": phone,
                "msg": f"Your OTP code is {otp}"
            }
            response = requests.get(url, params=params)

            if response.status_code == 200:
                return True, "Message sent successfully"
            else:
                return False, f"Failed to send message: {response.text}"

        except requests.RequestException as e:
            return False, str(e)

    @staticmethod
    def verify_code(phone, code):
        stored_otp = cache.get(phone)  # Retrieve stored OTP

        if stored_otp is None:
            return False, "OTP expired or not found"

        if stored_otp == code:
            cache.delete(phone)  # Remove OTP after successful verification
            return True, None
        else:
            return False, "Invalid OTP"

    @staticmethod
    def create_complaint(phoneNumber, vehicleNumber):
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
                        {'id': 68, 'name': "Role", 'value': "General Public"}
                    ]
                }
            }

        # api_key = JWTUtils.get_api_key_from_token(token)
        api_key = API_KEY

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