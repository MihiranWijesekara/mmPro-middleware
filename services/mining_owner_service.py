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
#methana thmi hadann tiyenne token eke ena payload ekt anuwa
            # Hardcoded NIC value
            OwnerName="Pasindu Lakshan"

            # Filter the issues based on the hardcoded NIC
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
