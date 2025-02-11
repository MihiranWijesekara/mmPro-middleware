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

            # Define query parameters for project_id=31 and tracker_id=8 (TPL)
            params = {
                "project_id": 31,
                "tracker_id": 8  # TPL tracker ID
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

            # Hardcoded Owner Name (could be dynamically retrieved from a token in the future)
            OwnerName = "Pasindu Lakshan" 

            # Filter the issues based on the hardcoded OwnerName
            filtered_issues = [
                issue for issue in issues if MLOwnerService.issue_belongs_to_nic(issue, OwnerName)
            ]

            return filtered_issues, None  # Returning filtered issues and no error

        except Exception as e:
            return None, f"Server error: {str(e)}"

    @staticmethod
    def issue_belongs_to_nic(issue, nic):
        """
        Check if the issue belongs to the NIC.
        This assumes that the NIC is stored in the custom fields list of the issue.
        """
        # Assuming NIC is stored in a custom field at index 0
        custom_fields = issue.get('custom_fields', [])
        
        if custom_fields:
            # Check if the NIC value matches in the custom field
            nic_value = custom_fields[0].get('value')
            if nic_value == nic:
                return True
        return False

    @staticmethod
    def create_tpl(data):
        try:
            REDMINE_URL = os.getenv("REDMINE_URL")
            API_KEY = os.getenv("REDMINE_API_KEY")

            if not REDMINE_URL or not API_KEY:
                return None, "Redmine URL or API Key is missing"

            headers = {
                "X-Redmine-API-Key": API_KEY,
                "Content-Type": "application/json"
            }

            # Sending POST request to Redmine to create the issue
            response = requests.post(
                f"{REDMINE_URL}/issues.json",
                json=data,
                headers=headers
            )

            if response.status_code != 201:
                return None, f"Failed to create issue: {response.status_code} - {response.text}"

            issue = response.json().get("issue", {})
            return issue, None  # Returning created issue and no error

        except Exception as e:
            return None, f"Server error: {str(e)}"
