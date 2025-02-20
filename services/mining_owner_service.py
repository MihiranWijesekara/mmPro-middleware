import requests
import os
from dotenv import load_dotenv
from datetime import datetime
from utils.jwt_utils import JWTUtils
from utils.MLOUtils import MLOUtils
from flask import request

load_dotenv()

class MLOwnerService:

    @staticmethod
    def mining_licenses(token):
        try:
            REDMINE_URL = os.getenv("REDMINE_URL")
            API_KEY = JWTUtils.get_api_key_from_token(token)

            if not REDMINE_URL or not API_KEY:
                return None, "Redmine URL or API Key is missing"

            # Step 1: Extract user_id from the token
            user_id, error = MLOUtils.get_user_info_from_token(token)
            if not user_id:
                return None, error

            # Debugging: Print the user_id
            print(f"User ID from token: {user_id}")

            # Step 2: Define query parameters for project_id=31 and tracker_id=7 (ML)
            params = {
                "project_id": 31,
                "tracker_id": 7  # ML tracker ID
            }

            headers = {
                "X-Redmine-API-Key": API_KEY
            }

            # Make the Redmine request
            response = requests.get(
                f"{REDMINE_URL}/projects/gsmb/issues.json",
                params=params,
                headers=headers
            )

            # Check if the request was successful
            if response.status_code != 200:
                return None, f"Failed to fetch issues: {response.status_code} - {response.text}"

            issues = response.json().get("issues", [])

            # Debugging: Print the issues to see if there are any
            print("Redmine Issues:", issues)

            # Step 3: Filter the issues based on the logged-in user's user_id
            filtered_issues = [
                issue for issue in issues if MLOUtils.issue_belongs_to_user(issue, user_id)
            ]

            # Debugging: Print the filtered issues to verify the result
            print("Filtered Issues:", filtered_issues)

            # Only return relevant issue details like subject, description, dates, etc.
            relevant_issues = [
                {
                    "subject": issue.get("subject"),
                    "status": issue.get("status"),
                    "description": issue.get("description"),
                    "start_date": issue.get("start_date"),
                    "due_date": issue.get("due_date"),
                    "done_ratio": issue.get("done_ratio"),
                    "is_private": issue.get("is_private"),
                    "estimated_hours": issue.get("estimated_hours"),
                    "total_estimated_hours": issue.get("total_estimated_hours"),
                    "custom_fields": issue.get("custom_fields")
                }
                for issue in filtered_issues
            ]

            # Return the relevant issue data
            return relevant_issues, None  # Returning filtered issues and no error

        except Exception as e:
            return None, f"Server error: {str(e)}"

    # Home function (mining_homeLicenses)
    @staticmethod
    def mining_homeLicenses(token):
        try:
            REDMINE_URL = os.getenv("REDMINE_URL")
            API_KEY = JWTUtils.get_api_key_from_token(token)

            if not REDMINE_URL or not API_KEY:
                return None, "Redmine URL or API Key is missing"

            # Step 1: Extract user_id from the token
            user_id, error = MLOUtils.get_user_info_from_token(token)
            if not user_id:
                return None, error

            # Debugging: Print the user_id
            print(f"User ID from token: {user_id}")

            # Step 2: Define query parameters for project_id=31 and tracker_id=7 (ML)
            params = {
                "project_id": 31,
                "tracker_id": 7  # ML tracker ID
            }

            headers = {
                "X-Redmine-API-Key": API_KEY
            }

            # Make the Redmine request
            response = requests.get(
                f"{REDMINE_URL}/projects/gsmb/issues.json",
                params=params,
                headers=headers
            )

            # Check if the request was successful
            if response.status_code != 200:
                return None, f"Failed to fetch issues: {response.status_code} - {response.text}"

            issues = response.json().get("issues", [])

            # Debugging: Print the issues to see if there are any
            print("Redmine Issues:", issues)

            # Step 3: Filter the issues based on the logged-in user's user_id
            filtered_issues = [
                issue for issue in issues if MLOUtils.issue_belongs_to_user(issue, user_id)
            ]

            # Debugging: Print the filtered issues to verify the result
            print("Filtered Issues:", filtered_issues)

            # Step 4: Further filter the issues based on the conditions:
            # - Valid status (not "Expired", "Closed", etc.)
            # - Sort by most recent due_date
            # - Limit to 5 issues

            valid_statuses = ["Valid"]  # Define valid statuses as per your requirements
            valid_issues = [
                issue for issue in filtered_issues
                if issue.get("status", {}).get("name") in valid_statuses
            ]

            # Sort by due_date in descending order to get the most recent issues first
            valid_issues_sorted = sorted(valid_issues, key=lambda x: datetime.strptime(x["due_date"], "%Y-%m-%d") if x.get("due_date") else datetime.min, reverse=True)

            # Limit to a maximum of 5 issues
            top_5_issues = valid_issues_sorted[:5]

            # Only return relevant issue details like subject, description, dates, etc.
            relevant_issues = [
                {
                    "subject": issue.get("subject"),
                    "status": issue.get("status"),
                    "description": issue.get("description"),
                    "start_date": issue.get("start_date"),
                    "due_date": issue.get("due_date"),
                    "done_ratio": issue.get("done_ratio"),
                    "is_private": issue.get("is_private"),
                    "estimated_hours": issue.get("estimated_hours"),
                    "total_estimated_hours": issue.get("total_estimated_hours"),
                    "custom_fields": issue.get("custom_fields")
                }
                for issue in top_5_issues
            ]

            # Return the relevant issue data
            return relevant_issues, None  # Returning filtered issues and no error

        except Exception as e:
            return None, f"Server error: {str(e)}"

    @staticmethod
    def view_tpls(token):
        try:
            REDMINE_URL = os.getenv("REDMINE_URL")
            API_KEY = JWTUtils.get_api_key_from_token(token)

            if not REDMINE_URL or not API_KEY:
                return None, "Redmine URL or API Key is missing"

            # Step 1: Extract user_id from the token
            user_id, error = MLOUtils.get_user_info_from_token(token)
            if not user_id:
                return None, error

            # Step 2: Define query parameters for project_id=31 and tracker_id=8 (TPL)
            params = {
                "project_id": 31,
                "tracker_id": 8  # TPL tracker ID
            }

            headers = {
                "X-Redmine-API-Key": API_KEY
            }

            # Make the Redmine request
            response = requests.get(
                f"{REDMINE_URL}/projects/gsmb/issues.json",
                params=params,
                headers=headers
            )

            # Check if the request was successful
            if response.status_code != 200:
                return None, f"Failed to fetch issues: {response.status_code} - {response.text}"

            issues = response.json().get("issues", [])

            # Filter the issues based on the user_id, if any
            filtered_issues = [
                issue for issue in issues if MLOUtils.issue_belongs_to_user(issue, user_id)
            ]

            # Debugging: Print the filtered issues to verify the result
            print("Filtered Issues:", filtered_issues)

            return filtered_issues, None  # Returning filtered issues and no error

        except Exception as e:
            return None, f"Server error: {str(e)}"
