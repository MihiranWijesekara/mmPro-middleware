import requests
import os
from dotenv import load_dotenv
from utils.jwt_utils import JWTUtils

load_dotenv()

class GsmbManagmentService:
    @staticmethod
    def monthly_total_sand_cubes(token):
        try:
            REDMINE_URL = os.getenv("REDMINE_URL")
            api_key = JWTUtils.get_api_key_from_token(token)

            if not REDMINE_URL:
                return None, "Redmine URL is missing"

            if not api_key:
                return None, "API Key is missing"

            params = {
                "project_id": 31,
                "tracker_id": 8  # tpl
            }

            headers = {
                "X-Redmine-API-Key": api_key,
                "Content-Type": "application/json"
            }

            url = f"{REDMINE_URL}/issues.json"
            response = requests.get(url, headers=headers, params=params)

            if response.status_code != 200:
                return None, f"Failed to fetch issues: {response.status_code} - {response.text}"

            issues = response.json().get("issues", [])

            # Initialize monthly data dictionary
            monthly_data = {
                "Jan": 0, "Feb": 0, "Mar": 0, "Apr": 0, "May": 0, "Jun": 0,
                "Jul": 0, "Aug": 0, "Sep": 0, "Oct": 0, "Nov": 0, "Dec": 0
            }

            # Process issues to calculate monthly cubes
            for issue in issues:
                custom_fields = issue.get("custom_fields", [])
                cube_field = next(
                    (field for field in custom_fields if field.get("id") == 15 and field.get("name") == "Cubes"), None
                )

                if cube_field and cube_field.get("value"):
                    issue_date = issue.get("created_on")
                    if issue_date:
                        month_index = int(issue_date[5:7]) - 1  # Extract month from YYYY-MM-DD
                        month_name = list(monthly_data.keys())[month_index]
                        monthly_data[month_name] += float(cube_field["value"])

            # Ensure the order is sorted by months correctly
            ordered_months = ["Jan", "Feb", "Mar", "Apr", "May", "Jun",
                              "Jul", "Aug", "Sep", "Oct", "Nov", "Dec"]

            sorted_monthly_data = {month: monthly_data[month] for month in ordered_months}

            return sorted_monthly_data, None

        except Exception as e:
            return None, f"Server error: {str(e)}"


    def fetch_top_mining_holders(token):
        try:
            REDMINE_URL = os.getenv("REDMINE_URL")
            api_key = JWTUtils.get_api_key_from_token(token)

            if not REDMINE_URL:
                return None, "Redmine URL is missing"

            if not api_key:
                return None, "API Key is missing"

            params = {
                "project_id": 31,
                "tracker_id": 7  # Assuming 7 is the tracker for Mining Licenses (adjust as needed)
            }

            headers = {
                "X-Redmine-API-Key": api_key,
                "Content-Type": "application/json"
            }

            url = f"{REDMINE_URL}/issues.json"
            response = requests.get(url, headers=headers, params=params)

            if response.status_code != 200:
                return None, f"Failed to fetch issues: {response.status_code} - {response.text}"

            issues = response.json().get("issues", [])

            mining_data = []

            # Process the issues to get the relevant data
            for issue in issues:
                custom_fields = issue.get("custom_fields", [])
                owner = next(
                    (field.get("value") for field in custom_fields if field.get("name") == "Owner Name"), None
                )

                # Ensure 'Capacity' and 'Used' are converted properly, check for empty values
                capacity_str = next(
                    (field.get("value") for field in custom_fields if field.get("name") == "Capacity"), None
                )
                used_str = next(
                    (field.get("value") for field in custom_fields if field.get("name") == "Used"), None
                )

                # Convert to float only if the string is a valid number or default to 0
                capacity = float(capacity_str) if capacity_str and capacity_str.strip() != "" else 0
                used = float(used_str) if used_str and used_str.strip() != "" else 0

                if owner and capacity > 0:
                    percentage_used = ((used / capacity) * 100) if capacity else 0
                    mining_data.append({"label": owner, "value": round(percentage_used, 2), "capacity": capacity})

            # Sort by capacity (in descending order) and get top 10
            mining_data.sort(key=lambda x: x['capacity'], reverse=True)
            return mining_data[:10], None

        except Exception as e:
            return None, f"Server error: {str(e)}"
    
    def fetch_royalty_counts(token):  