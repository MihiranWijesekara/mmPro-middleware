import requests
import os
from dotenv import load_dotenv
import json
from datetime import datetime

from utils.jwt_utils import JWTUtils


load_dotenv()

class GsmbOfficerService:
    @staticmethod
    def get_Issues_Data():
        try:
            REDMINE_URL = os.getenv("REDMINE_URL")
            API_KEY = os.getenv("REDMINE_ADMIN_API_KEY")

            if not REDMINE_URL or not API_KEY:
                return None, "Redmine URL or API Key is missing"

            # Define query parameters for project_id=31 and tracker_id=7
            params = {
                "project_id": 31,
                "tracker_id": 7
            }

            headers = {
                "X-Redmine-API-Key": API_KEY
            }

            response = requests.get(
                f"{REDMINE_URL}/issues.json",
                params=params,
                headers=headers
            )

            if response.status_code != 200:
                return None, f"Failed to fetch issues: {response.status_code} - {response.text}"

            issues = response.json().get("issues", [])

            return issues, None  # Returning the list of issues and no error

        except Exception as e:
            return None, f"Server error: {str(e)}"
