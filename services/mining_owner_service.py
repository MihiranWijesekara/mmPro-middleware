import requests
import os
from dotenv import load_dotenv

load_dotenv()

class MLOwnerService:
    @staticmethod
    def mining_licenses():
        try:
            REDMINE_URL = os.getenv("REDMINE_URL")
            API_KEY = os.getenv("REDMINE_API_KEY")

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
