import requests
import os
from dotenv import load_dotenv
from utils.jwt_utils import JWTUtils
from flask import jsonify


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

            # Convert the dictionary to a list of objects in the correct order
            ordered_months = ["Jan", "Feb", "Mar", "Apr", "May", "Jun",
                            "Jul", "Aug", "Sep", "Oct", "Nov", "Dec"]

            formatted_data = [
                {"month": month, "totalCubes": monthly_data[month]}
                for month in ordered_months
            ]

            return formatted_data, None

        except Exception as e:
            return None, f"Server error: {str(e)}"

    @staticmethod
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


    @staticmethod
    def fetch_royalty_counts(token):
        try:
            REDMINE_URL = os.getenv("REDMINE_URL")
            api_key = JWTUtils.get_api_key_from_token(token)

            if not REDMINE_URL:
                return None, "Redmine URL is missing"

            if not api_key:
                return None, "API Key is missing"

            total_royalty = 0
            fetched_orders = []

            params = {
                "project_id": 31,  # Assuming this is the project ID
                "tracker_id": 7,   # Assuming 7 is the tracker for Mining Licenses (adjust as needed)
            }

            headers = {
                "X-Redmine-API-Key": api_key,
                "Content-Type": "application/json"
            }

            url = f"{REDMINE_URL}/issues.json"
            response = requests.get(url, headers=headers, params=params)

            if response.status_code != 200:
                return None, f"Failed to fetch issues: {response.status_code} - {response.text}"

            data = response.json()
            issues = data.get('issues', [])

            # Filter issues by tracker ID 7 and tracker name 'ML' and status name 'Valid'
            filtered_issues = [
                issue for issue in issues 
                if issue.get("tracker", {}).get("id") == 7 
                and issue.get("tracker", {}).get("name") == "ML"
                and issue.get("status", {}).get("name") == "Valid"
            ]

            # Sum up the royalties
            for issue in filtered_issues:
                royalty_field = next(
                    (field for field in issue.get("custom_fields", []) if field.get("name") == "Royalty(sand)due"),
                    None
                )

                royalty_value = 0
                if royalty_field:
                    try:
                        royalty_value = float(royalty_field.get("value", "0") or "0")  # Default empty value to "0"
                    except ValueError:
                        royalty_value = 0  # Ignore if conversion fails

                if royalty_value > 0:  # Exclude royalty = 0
                    total_royalty += royalty_value

                    # Prepare the order details
                    fetched_orders.append({
                        "title": issue.get("assigned_to", {}).get("name", "Unknown"),
                        "description": f"Royalty: {royalty_value}",
                        "avatar": "https://via.placeholder.com/40",
                    })

            # Return the response as JSON
            return jsonify({
                "total_royalty": total_royalty,
                "orders": fetched_orders
            }), None  # Return data and no error

        except Exception as e:
            print("Error fetching royalty data:", e)
            return None, "An error occurred while fetching data"

            
    @staticmethod
    def monthly_mining_license_count(token):
        try:
            REDMINE_URL = os.getenv("REDMINE_URL")
            api_key = JWTUtils.get_api_key_from_token(token)

            if not REDMINE_URL:
                return None, "Redmine URL is missing"

            if not api_key:
                return None, "API Key is missing"

            headers = {
                "Content-Type": "application/json",
                "X-Redmine-API-Key": api_key
            }

            license_counts = {}
            page = 1
            has_more_data = True

            while has_more_data:
                response = requests.get(
                    f"{REDMINE_URL}/issues.json?page={page}",
                    headers=headers
                )

                if response.status_code != 200:
                    return None, f"Failed to fetch data from Redmine: {response.status_code}"

                data = response.json()
                issues = data.get("issues", [])

                if not issues:
                    has_more_data = False
                    break

                for issue in issues:
                    if issue.get("tracker", {}).get("id") == 7 and issue.get("tracker", {}).get("name") == "ML":
                        created_date = issue.get("created_on")
                        if created_date:
                            month = created_date.split("-")[1]  # Extract month from date
                            license_counts[month] = license_counts.get(month, 0) + 1

                page += 1

            formatted_data = [
                {"month": "Jan", "miningLicense": license_counts.get("01", 0)},
                {"month": "Feb", "miningLicense": license_counts.get("02", 0)},
                {"month": "Mar", "miningLicense": license_counts.get("03", 0)},
                {"month": "Apr", "miningLicense": license_counts.get("04", 0)},
                {"month": "May", "miningLicense": license_counts.get("05", 0)},
                {"month": "Jun", "miningLicense": license_counts.get("06", 0)},
                {"month": "Jul", "miningLicense": license_counts.get("07", 0)},
                {"month": "Aug", "miningLicense": license_counts.get("08", 0)},
                {"month": "Sep", "miningLicense": license_counts.get("09", 0)},
                {"month": "Oct", "miningLicense": license_counts.get("10", 0)},
                {"month": "Nov", "miningLicense": license_counts.get("11", 0)},
                {"month": "Dec", "miningLicense": license_counts.get("12", 0)},
            ]

            return formatted_data, None

        except Exception as e:
            return None, str(e)


    @staticmethod
    def transport_license_destination(token):
        try:
            REDMINE_URL = os.getenv("REDMINE_URL")
            api_key = JWTUtils.get_api_key_from_token(token)

            if not REDMINE_URL:
                return None, "Redmine URL is missing"

            if not api_key:
                return None, "API Key is missing"

            params = {
                "project_id": 31,  # Assuming project ID for GSMB
                "tracker_id": 8    # Assuming tracker ID for transport licenses
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

            # Aggregate data by destination (Location)
            destination_counts = {}
            for issue in issues:
                custom_fields = issue.get("custom_fields", [])
                location_field = next(
                    (field for field in custom_fields if field.get("name") == "Location"), None
                )

                if location_field and location_field.get("value"):
                    destination = location_field["value"]
                    destination_counts[destination] = destination_counts.get(destination, 0) + 1

            # Format the data for the frontend
            formatted_data = [
                {"name": destination, "value": count}
                for destination, count in destination_counts.items()
            ]

            return formatted_data, None

        except Exception as e:
            return None, f"Server error: {str(e)}"   


    @staticmethod
    def total_location_ml(token):
        try:
            REDMINE_URL = os.getenv("REDMINE_URL")
            api_key = JWTUtils.get_api_key_from_token(token)

            if not REDMINE_URL:
                return None, "Redmine URL is missing"

            if not api_key:
                return None, "API Key is missing"

            params = {
                "project_id": 31,  # Assuming project ID for GSMB
                "tracker_id": 7     # Assuming tracker ID for mining licenses
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

            # Aggregate data by location
            location_counts = {}
            for issue in issues:
                custom_fields = issue.get("custom_fields", [])
                location_field = next(
                    (field for field in custom_fields if field.get("name") == "Location"), None
                )

                if location_field and location_field.get("value"):
                    location = location_field["value"]
                    location_counts[location] = location_counts.get(location, 0) + 1

            # Format the data for the frontend
            formatted_data = [
                {"name": location, "value": count}
                for location, count in location_counts.items()
            ]

            return formatted_data, None

        except Exception as e:
            return None, f"Server error: {str(e)}"            

     
    @staticmethod
    def complaint_counts(token):
        try:
            REDMINE_URL = os.getenv("REDMINE_URL")
            api_key = JWTUtils.get_api_key_from_token(token)

            if not REDMINE_URL:
                return None, "Redmine URL is missing"

            if not api_key:
                return None, "API Key is missing"

            params = {
                "project_id": 31,  # Assuming project ID for GSMB
                "tracker_id": 26    # Assuming tracker ID for complaints
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

            # Initialize counts
            counts = {
                "New": 0,
                "Rejected": 0,
                "InProgress": 0,
                "Executed": 0,
                "total": 0
            }

            # Process issues to count complaints by status
            for issue in issues:
                status = issue.get("status", {}).get("name", "")
                if status == "New":
                    counts["New"] += 1
                elif status == "Rejected":
                    counts["Rejected"] += 1
                elif status == "In Progress":
                    counts["InProgress"] += 1
                elif status == "Executed":
                    counts["Executed"] += 1

            counts["total"] = len(issues)

            return counts, None

        except Exception as e:
            return None, f"Server error: {str(e)}"  

    
    @staticmethod
    def role_counts(token):
        try:
            REDMINE_URL = os.getenv("REDMINE_URL")
            api_key = JWTUtils.get_api_key_from_token(token)

            if not REDMINE_URL:
                return None, "Redmine URL is missing"

            if not api_key:
                return None, "API Key is missing"

            headers = {
                "X-Redmine-API-Key": api_key,
                "Content-Type": "application/json"
            }

            url = f"{REDMINE_URL}/projects/GSMB/memberships.json"
            response = requests.get(url, headers=headers)

            if response.status_code != 200:
                return None, f"Failed to fetch memberships: {response.status_code} - {response.text}"

            memberships = response.json().get("memberships", [])

            # Initialize counts
            counts = {
                "licenceOwner": 0,
                "activeGSMBOfficers": 0,
                "policeOfficers": 0,
                "public": 0
            }

            # Process memberships to count roles
            for membership in memberships:
                roles = membership.get("roles", [])
                if roles:
                    role_name = roles[0].get("name", "")
                    if role_name == "MLOwner":
                        counts["licenceOwner"] += 1
                    elif role_name == "GSMBOfficer":
                        counts["activeGSMBOfficers"] += 1
                    elif role_name == "PoliceOfficer":
                        counts["policeOfficers"] += 1
                    elif role_name == "Public":
                        counts["public"] += 1

            return counts, None

        except Exception as e:
            return None, f"Server error: {str(e)}"


    @staticmethod
    def mining_license_count(token):
        try:
            REDMINE_URL = os.getenv("REDMINE_URL")
            api_key = JWTUtils.get_api_key_from_token(token)

            if not REDMINE_URL:
                return None, "Redmine URL is missing"

            if not api_key:
                return None, "API Key is missing"

            params = {
                "project_id": 31,  # Assuming project ID for GSMB
                "tracker_id": 7     # Assuming tracker ID for mining licenses
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

            # Initialize counts
            counts = {
                "valid": 0,
                "expired": 0,
                "rejected": 0,
                "total": 0
            }

            # Process issues to count mining licenses by status
            for issue in issues:
                status = issue.get("status", {}).get("name", "")
                if status == "Valid":
                    counts["valid"] += 1
                elif status == "Expired":
                    counts["expired"] += 1
                elif status == "Rejected":
                    counts["rejected"] += 1

            counts["total"] = len(issues)

            return counts, None

        except Exception as e:
            return None, f"Server error: {str(e)}"       