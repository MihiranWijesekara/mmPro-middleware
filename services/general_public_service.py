import os
import requests
from dotenv import load_dotenv

load_dotenv()

class GeneralPublicService:
    @staticmethod
    def is_lorry_number_valid(lorry_number):
        try:
            REDMINE_URL = os.getenv("REDMINE_URL")
            API_KEY = os.getenv("REDMINE_ADMIN_API_KEY")

            if not REDMINE_URL or not API_KEY:
                return None, "Redmine URL or API Key is missing"

            headers = {"X-Redmine-API-Key": API_KEY}

            # Fetch all TPL licenses (tracker_id = 8)
            tpl_params = {"tracker_id": 8}
            tpl_response = requests.get(f"{REDMINE_URL}/issues.json", params=tpl_params, headers=headers)

            if tpl_response.status_code != 200:
                return None, f"Failed to fetch TPL issues: {tpl_response.status_code} - {tpl_response.text}"

            tpl_issues = tpl_response.json().get("issues", [])

            # Check if any TPL license matches the given lorry number (cf_13)
            tpl_license_exists = any(
                any(cf["id"] == 13 and cf["value"] == lorry_number for cf in issue.get("custom_fields", []))
                for issue in tpl_issues
            )

            return tpl_license_exists, None  # Return True if exists, False if not

        except Exception as e:
            return None, f"Server error: {str(e)}"
