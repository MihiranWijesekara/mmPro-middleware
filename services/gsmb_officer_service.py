import requests
import os
from dotenv import load_dotenv
import json
from datetime import datetime
from utils.jwt_utils import JWTUtils
from utils.MLOUtils import MLOUtils
from flask import request

from utils.limit_utils import LimitUtils

load_dotenv()

class GsmbOfficerService:

    ORS_API_KEY = os.getenv("ORS_API_KEY")
    
    @staticmethod
    def get_mlowners(token):
        try:
            # 🔑 Extract user's API key from token for memberships request
            user_api_key = JWTUtils.get_api_key_from_token(token)
            print(user_api_key)
            if not user_api_key:
                return None, "Invalid or missing API key in the token"

            # 🔑 Get Redmine Admin API key for user details request
            admin_api_key = os.getenv("REDMINE_ADMIN_API_KEY")
            if not admin_api_key:
                return None, "Environment variable 'REDMINE_ADMIN_API_KEY' is not set"

            # 🌐 Get Redmine URL
            REDMINE_URL = os.getenv("REDMINE_URL")
            print(REDMINE_URL)
            if not REDMINE_URL:
                return None, "Environment variable 'REDMINE_URL' is not set"

            # 1️⃣ Fetch memberships using the **user's API key**
            memberships_url = f"{REDMINE_URL}/projects/mmpro-gsmb/memberships.json"
            memberships_response = requests.get(
                memberships_url, 
                headers={"X-Redmine-API-Key": user_api_key, "Content-Type": "application/json"}
            )

            if memberships_response.status_code != 200:
                return None, f"Failed to fetch memberships: {memberships_response.status_code} - {memberships_response.text}"

            memberships = memberships_response.json().get("memberships", [])

            # 2️⃣ Filter users who have the role "MLOwner"
            ml_owner_ids = [
                membership['user']['id'] for membership in memberships
                if any(role["name"] == "MLOwner" for role in membership.get("roles", []))
            ]

            if not ml_owner_ids:
                return [], None  # No MLOwner users found

            # 3️⃣ Fetch user details using the **admin API key** (for broader access)
            users_url = f"{REDMINE_URL}/users.json?status=1&limit=100"
            users_response = requests.get(
                users_url, 
                headers={"X-Redmine-API-Key": admin_api_key, "Content-Type": "application/json"}
            )

            if users_response.status_code != 200:
                return None, f"Failed to fetch user details: {users_response.status_code} - {users_response.text}"

            all_users = users_response.json().get("users", [])

            # 4️⃣ Filter users who match MLOwner IDs
            ml_owners_details = [
                user for user in all_users if user["id"] in ml_owner_ids
            ]

            return ml_owners_details, None  # ✅ Return only relevant user details

        except Exception as e:
            return None, f"Server error: {str(e)}"
        


    @staticmethod
    def get_tpls(token):
        try:
            # 🔑 Extract user's API key from token
            user_api_key = JWTUtils.get_api_key_from_token(token)
            if not user_api_key:
                return None, "Invalid or missing API key in the token"

            REDMINE_URL = os.getenv("REDMINE_URL")
            if not REDMINE_URL:
                return None, "Environment variable 'REDMINE_URL' is not set"

            # 🚀 Fetch TPL issues from Redmine
            tpl_issues_url = f"{REDMINE_URL}/issues.json?tracker_id=5&project_id=1"
            response = requests.get(
                tpl_issues_url,
                headers={"X-Redmine-API-Key": user_api_key, "Content-Type": "application/json"}
            )

            if response.status_code != 200:
                return None, f"Failed to fetch TPL issues: {response.status_code} - {response.text}"

            issues = response.json().get("issues", [])
            formatted_tpls = []

            for issue in issues:
                formatted_tpl = {
                    "id": issue.get("id"),
                    "subject": issue.get("subject"),
                    "status": issue.get("status", {}).get("name"),
                    "author": issue.get("author", {}).get("name"),
                    "tracker": issue.get("tracker", {}).get("name"),
                    "assigned_to": issue.get("assigned_to", {}).get("name") if issue.get("assigned_to") else None,
                    "start_date": issue.get("start_date"),
                    "due_date": issue.get("due_date"),
                    "lorry_number": GsmbOfficerService.get_custom_field_value(issue.get("custom_fields", []), "Lorry Number"),
                    "driver_contact": GsmbOfficerService.get_custom_field_value(issue.get("custom_fields", []), "Driver Contact"),
                    "cubes": GsmbOfficerService.get_custom_field_value(issue.get("custom_fields", []), "Cubes"),
                    "mining_license_number": GsmbOfficerService.get_custom_field_value(issue.get("custom_fields", []), "Mining License Number"),
                    "destination": GsmbOfficerService.get_custom_field_value(issue.get("custom_fields", []), "Destination"),
                    "lorry_driver_name": GsmbOfficerService.get_custom_field_value(issue.get("custom_fields", []), "Lorry Driver Name"),
                
                }
                formatted_tpls.append(formatted_tpl)

            return formatted_tpls, None

        except Exception as e:
            return None, f"Server error: {str(e)}"
        
    @staticmethod
    def get_mining_licenses(token):
        try:
            # 🔑 Extract user's API key from token
            user_api_key = JWTUtils.get_api_key_from_token(token)
            if not user_api_key:
                return None, "Invalid or missing API key in the token"

            # 🌐 Get Redmine URL
            REDMINE_URL = os.getenv("REDMINE_URL")
            if not REDMINE_URL:
                return None, "Environment variable 'REDMINE_URL' is not set"

            # 🚀 Fetch ML issues from Redmine
            ml_issues_url = f"{REDMINE_URL}/issues.json?tracker_id=4&project_id=1"
            response = requests.get(
                ml_issues_url,
                headers={"X-Redmine-API-Key": user_api_key, "Content-Type": "application/json"}
            )

            if response.status_code != 200:
                return None, f"Failed to fetch ML issues: {response.status_code} - {response.text}"

            # 🛠️ Process the response
            issues = response.json().get("issues", [])
            formatted_mls = []

            for issue in issues:
                formatted_ml = {
                    "id": issue.get("id"),
                    "subject": issue.get("subject"),
                    "status": issue.get("status", {}).get("name"),
                    "author": issue.get("author", {}).get("name"),
                    "assigned_to": issue.get("assigned_to", {}).get("name") if issue.get("assigned_to") else None,
                    "start_date": issue.get("start_date"),
                    "due_date": issue.get("due_date"),
                    "exploration_licence_no": GsmbOfficerService.get_custom_field_value(issue.get("custom_fields", []), "Exploration Licence No"),
                    "applicant_or_company_name": GsmbOfficerService.get_custom_field_value(issue.get("custom_fields", []), "Name of Applicant OR Company"),
                    "land_name": GsmbOfficerService.get_custom_field_value(issue.get("custom_fields", []), "Land Name(Licence Details) "),
                    "land_owner_name": GsmbOfficerService.get_custom_field_value(issue.get("custom_fields", []), "Land owners’ name"),
                    "village_name": GsmbOfficerService.get_custom_field_value(issue.get("custom_fields", []), "Name of village "),
                    "grama_niladhari_division": GsmbOfficerService.get_custom_field_value(issue.get("custom_fields", []), "Grama Niladhari Division"),
                    "divisional_secretary_division": GsmbOfficerService.get_custom_field_value(issue.get("custom_fields", []), "Divisional Secretary Division"),
                    "administrative_district": GsmbOfficerService.get_custom_field_value(issue.get("custom_fields", []), "Administrative District"),
                    "capacity": GsmbOfficerService.get_custom_field_value(issue.get("custom_fields", []), "Capacity"),
                    "used": GsmbOfficerService.get_custom_field_value(issue.get("custom_fields", []), "Used"),
                    "remaining": GsmbOfficerService.get_custom_field_value(issue.get("custom_fields", []), "Remaining"),
                    "mobile_number": GsmbOfficerService.get_custom_field_value(issue.get("custom_fields", []), "Mobile Number"),
                    "royalty": GsmbOfficerService.get_custom_field_value(issue.get("custom_fields", []), "Royalty"),
                
                }
                formatted_mls.append(formatted_ml)

            return formatted_mls, None

        except Exception as e:
            return None, f"Server error: {str(e)}"

    @staticmethod
    def get_custom_field_value(custom_fields, field_name):
        """Helper function to extract custom field value by name."""
        for field in custom_fields:
            if field.get("name") == field_name:
                return field.get("value")
        return None
    @staticmethod
    def get_mining_license_counts(token):
        try:
            # 🔑 Extract user's API key from token
            user_api_key = JWTUtils.get_api_key_from_token(token)
            if not user_api_key:
                return None, "Invalid or missing API key in the token"

            # 🌐 Get Redmine URL
            REDMINE_URL = os.getenv("REDMINE_URL")
            if not REDMINE_URL:
                return None, "Environment variable 'REDMINE_URL' is not set"

            # 🚀 Fetch ML issues from Redmine
            ml_issues_url = f"{REDMINE_URL}/issues.json?tracker_id=4&project_id=1"
            response = requests.get(
                ml_issues_url,
                headers={"X-Redmine-API-Key": user_api_key, "Content-Type": "application/json"}
            )

            if response.status_code != 200:
                return None, f"Failed to fetch ML issues: {response.status_code} - {response.text}"

            # 🛠️ Process the response
            issues = response.json().get("issues", [])
            license_counts = {}

            for issue in issues:
                assigned_to = issue.get("assigned_to", {}).get("name", "Unassigned")  # Handle unassigned cases
                license_counts[assigned_to] = license_counts.get(assigned_to, 0) + 1

            return license_counts, None

        except Exception as e:
            return None, f"Server error: {str(e)}"
        

    @staticmethod
    def calculate_distance(city1, city2):
        """
        Calculate the distance between two cities using OpenRouteService API and return the time in hours.

        Args:
            city1 (str): Name of the first city.
            city2 (str): Name of the second city.

        Returns:
            dict: A dictionary containing the time in hours or an error message.
        """
        try:
            # Step 1: Geocode cities to get coordinates
            def geocode_location(city_name):
                print("first request ins")
                url = f"https://geocode.maps.co/search?q={city_name}&format=json"
                response_first = requests.get(url, timeout=1)
                response = response_first.json()        
                if response:
                    lat = float(response[0]['lat'])
                    lon = float(response[0]['lon'])
                    print(lat, lon)
                    return lon, lat  # Return as [longitude, latitude]
                else:
                    raise ValueError(f"Location '{city_name}' not found")

            # Geocode both cities
            coord1 = geocode_location(city1)
            coord2 = geocode_location(city2)

            print("second request")

            # Step 2: Calculate distance using OpenRouteService
            url = "https://api.openrouteservice.org/v2/directions/driving-car"
            headers = {
                "Authorization": GsmbOfficerService.ORS_API_KEY,
                "Content-Type": "application/json"
            }
            body = {
                "coordinates": [coord1, coord2],
                "units": "km"
            }
            response = requests.post(url, headers=headers, json=body).json()

            # Extract distance from the response
            distance_km = response['routes'][0]['summary']['distance']

            # Calculate the time in hours: (distance / 30 km/h) + 2 hours
            time_hours = (distance_km / 30) + 2

            # Return the time in hours
            return {
                "success": True,
                "city1": city1,
                "city2": city2,
                "time_hours": round(time_hours, 2)
            }
        except Exception as e:
            return {"success": False, "error": str(e)}



#     @staticmethod
#     def get_Issues_Data(token):  # Accept token as a parameter
#         try:
#             # Use the passed token here
#             api_key = JWTUtils.get_api_key_from_token(token)

#             if not api_key:
#                 return None, "API Key is missing"

#             REDMINE_URL = os.getenv("REDMINE_URL")

#             if not REDMINE_URL:
#                 return None, "Redmine URL is missing"

#             headers = {
#                 "X-Redmine-API-Key": api_key,
#                 "Content-Type": "application/json"
#             }

#             url = f"{REDMINE_URL}/projects/gsmb/issues.json"

#             response = requests.get(url, headers=headers)

#             if response.status_code != 200:
#                 return None, f"Failed to fetch issues: {response.status_code} - {response.text}"

#             issues = response.json().get("issues", [])

#             return issues, None  # Returning the list of issues and no error

#         except Exception as e:
#             return None, f"Server error: {str(e)}"




#     @staticmethod
#     def user_detail(user_id, token):
#         api_key = JWTUtils.get_api_key_from_token(token)
#         try:
#             REDMINE_URL = os.getenv("REDMINE_URL")

#             if not REDMINE_URL or not api_key:
#                 return None, "Redmine URL or API Key is missing"
#             headers = {
#                 "X-Redmine-API-Key": api_key,  # Include the token for authorization
#                 "Content-Type": "application/json"
#             }
#             url = f"{REDMINE_URL}/users/{user_id}.json"

#             response = requests.get(
#                 url,  # Ensure correct JSON structure
#                 headers=headers
#             )

#             if response.status_code != 200:
#                 return None, f"Failed to fetch issue: {response.status_code} - {response.text}"

#             user_detail = response.json().get("user", {})


#             return user_detail, None  # Returning filtered issues and no error

#         except Exception as e:
#             return None, f"Server error: {str(e)}"




#     @staticmethod
#     def add_new_license(token, payload):
#         try:
#             api_key = JWTUtils.get_api_key_from_token(token)

#             if not api_key:
#                 return None, "API Key is missing"

#             REDMINE_URL = os.getenv("REDMINE_URL")

#             if not REDMINE_URL:
#                 return None, "Redmine URL is missing"

#             headers = {
#                 "X-Redmine-API-Key": api_key,
#                 "Content-Type": "application/json"
#             }

#             url = f"{REDMINE_URL}/projects/gsmb/issues.json"

#             # Validate and extract necessary fields from the payload
#             issue_data = payload.get("issue", {})
#             project_id = issue_data.get("project", {}).get("id")
#             tracker_id = issue_data.get("tracker", {}).get("id")
#             subject = issue_data.get("subject")
#             status_id = issue_data.get("status", {}).get("id")
#             start_date = issue_data.get("start_date")
#             due_date = issue_data.get("due_date")
#             estimated_hours = issue_data.get("estimated_hours")
#             custom_fields = issue_data.get("custom_fields", [])

#             if not all([project_id, tracker_id, subject, status_id, start_date, due_date, estimated_hours]):
#               return None, "Missing required issue details"

#             # Prepare data to send to Redmine
#             data = {
#                 "issue": {
#                     "project_id": project_id,
#                     "tracker_id": tracker_id,
#                     "subject": subject,
#                     "status_id": status_id,
#                     "start_date": start_date,
#                     "due_date": due_date,
#                     "estimated_hours": estimated_hours,
#                     "custom_fields": custom_fields,
#                 }
#             }

#             response = requests.post(url, json=data, headers=headers)

#             if response.status_code != 201:
#                 return None, f"Failed to create license: {response.status_code} - {response.text}"

#             new_license = response.json().get("issue", {})
#             return new_license, None  # Returning the new license data and no error

#         except Exception as e:
#             return None, f"Server error: {str(e)}"
 



# # Get License details


#     @staticmethod
#     def get_license_details(token, licenseId):
        
        
#         try:
            
#             api_key = JWTUtils.get_api_key_from_token(token)
#             if not api_key:
#                 return None, "Invalid or missing API key in the token"

#             REDMINE_URL = os.getenv("REDMINE_URL")
#             if not REDMINE_URL:
#                return None, "Environment variable 'REDMINE_URL' is not set"

            
#             headers = {
#                 "X-Redmine-API-Key": api_key,  # Include the token for authorization
#                 "Content-Type": "application/json"
#             }
#             url = f"{REDMINE_URL}/issues/{licenseId}.json"

#             response = requests.get(
#                 url,  # Ensure correct JSON structure
#                 headers=headers
#             )

#             if response.status_code != 200:
#                 return None, f"Failed to fetch issue: {response.status_code} - {response.text}"

#             license_details = response.json().get("issue", {})  # Adjust according to actual JSON response structure
#             return license_details, None

#         except Exception as e:
#             return None, f"Server error: {str(e)}"









# # Update license



#     @staticmethod
#     def update_license(token, payload, licenseId):
#         try:
#             api_key = JWTUtils.get_api_key_from_token(token)

#             if not api_key:
#                 return None, "API Key is missing"

#             REDMINE_URL = os.getenv("REDMINE_URL")

#             if not REDMINE_URL:
#                 return None, "Redmine URL is missing"

#             headers = {
#                 "X-Redmine-API-Key": api_key,
#                 "Content-Type": "application/json"
#             }

#             url = f"{REDMINE_URL}/issues/{licenseId}.json"

#             # Validate and extract necessary fields from the payload
#             issue_data = payload.get("issue", {})
#             # project_id = issue_data.get("project", {}).get("id")
#             # tracker_id = issue_data.get("tracker", {}).get("id")
#             # subject = issue_data.get("subject")
#             # status_id = issue_data.get("status", {}).get("id")
#             # start_date = issue_data.get("start_date")
#             # due_date = issue_data.get("due_date")
#             # estimated_hours = issue_data.get("estimated_hours")
#             custom_fields = issue_data.get("custom_fields", [])

           
#             if not custom_fields:
#               return None, "No custom fields provided for update"

#             # Prepare data to send to Redmine
#             data = {
#                 "issue": {
#                     "custom_fields": custom_fields,
#                 }
#             }

#             response = requests.put(url, json=data, headers=headers)

#             if response.status_code == 204:
#                 return {"success": True, "message": "License updated successfully."}, None

#             if response.status_code != 200:
#                return None, f"Failed to update license: {response.status_code} - {response.text}"

#             updated_license = response.json().get("issue", {})
#             return updated_license, None

#         except Exception as e:
#            return None, f"Server error: {str(e)}"
        
    
    
    
    
    
#     @staticmethod
#     def add_new_mlowner(token,userData):
        
#         try:
#             api_key = JWTUtils.get_api_key_from_token(token)

#             if not api_key:
#                 return None, "API Key is missing"

#             REDMINE_URL = os.getenv("REDMINE_URL")

#             if not REDMINE_URL:
#                 return None, "Redmine URL is missing"

#             headers = {
#                 "X-Redmine-API-Key": api_key,
#                 "Content-Type": "application/json"
#             }

#             # Assume the userData payload looks like { 'user': { user_details_here } }
#             user_details = userData.get('user', {})
#             if not user_details:
#                 return None, "User data is missing in the request"

#             # You can expand this to match the structure your backend expects
#             payload = {
#                 "user": user_details
#             }

#             # Call the appropriate API or service to register the ML owner
#             url = f"{REDMINE_URL}/users.json"
#             response = requests.post(url, json=payload, headers=headers)

#             if response.status_code != 201:
#                 return None, f"Failed to add ML owner: {response.status_code} - {response.text}"

#             new_owner = response.json().get("user", {})
#             return new_owner, None

#         except Exception as e:
#             return None, f"Server error: {str(e)}"
        
        
        
        
    
#     @staticmethod
#     def assign_user_to_project(user_id, project_id, role_id, token):
#         try:
#             api_key = JWTUtils.get_api_key_from_token(token)

#             if not api_key:
#                 return None, "API Key is missing"

#             REDMINE_URL = os.getenv("REDMINE_URL")

#             if not REDMINE_URL:
#                 return None, "Redmine URL is missing"

#             headers = {
#                 "X-Redmine-API-Key": api_key,
#                 "Content-Type": "application/json"
#             }

#             # Prepare payload to assign user to project with the correct role
#             payload = {
#                 "membership": {
#                     "user_id": user_id,
#                     "role_ids": [role_id]  # Assign the correct role (ML Owner in this case)
#                 }
#             }

#             url = f"{REDMINE_URL}/projects/{project_id}/memberships.json"
#             response = requests.post(url, json=payload, headers=headers)

#             if response.status_code != 201:
#                 return None, f"Failed to assign user to project: {response.status_code} - {response.text}"

#             # Return the assignment details if successful
#             return response.json(), None

#         except Exception as e:
#             return None, f"Server error: {str(e)}"       








#     @staticmethod
#     def view_tpls(token):
#         try:
            
#             api_key = JWTUtils.get_api_key_from_token(token)
            
#             if not api_key:
#                 return None, "API Key is missing"
            
#             REDMINE_URL = os.getenv("REDMINE_URL")
            
#             if not REDMINE_URL:
#                 return None, "Redmine URL is missing"
            
#             headers ={
#                 "X-Redmine-API-Key": api_key,
#                 "Content-Type": "application/json"
#             }
            
#             # Fetch TPL issues from Redmine
#             url = f"{REDMINE_URL}/projects/gsmb/issues.json"  # Assuming TPL issues have tracker_id=9
#             response = requests.get(url, headers=headers)

#             if response.status_code != 200:
#                 return None, f"Failed to fetch TPL issues: {response.status_code} - {response.text}"

#             issues = response.json().get("issues", [])
#             return issues, None

            

#         except Exception as e:
#             return None, f"Server error: {str(e)}"










# Get mlowners old code


    # @staticmethod
    # def get_mlowners(token):
        
        
    #    try:
    #         api_key = JWTUtils.get_api_key_from_token(token)
    #         if not api_key:
    #             return None, "Invalid or missing API key in the token"

    #         REDMINE_URL = os.getenv("REDMINE_URL")
    #         if not REDMINE_URL:
    #             return None, "Environment variable 'REDMINE_URL' is not set"

    #         headers = {
    #             "X-Redmine-API-Key": api_key,  # Include the token for authorization
    #             "Content-Type": "application/json"
    #         }
    #         url = f"{REDMINE_URL}/projects/GSMB/memberships.json"
        
    #         response = requests.get(
    #             url,  # Ensure correct JSON structure
    #             headers=headers
    #         )

    #         if response.status_code != 200:
    #             return None, f"Failed to fetch issue: {response.status_code} - {response.text}"

    #         # Get all users in the GSMB project
    #         memberships = response.json().get("memberships", [])
            
    #         # Filter users by "MLOwner" role
    #         ml_owners = [
    #             membership for membership in memberships
    #             if any(role["name"] == "MLOwner" for role in membership.get("roles", []))
    #         ]
            
    #         # For each MLOwner, fetch their associated licenses and user details
    #         owners_with_details_and_licenses = []
    #         for owner in ml_owners:
    #             user_id = owner['user']['id']
                
    #             # Fetch user details
    #             user_response = requests.get(
    #                 f"{REDMINE_URL}/users/{user_id}.json",
    #                 headers=headers
    #             )
                
                

    #             if user_response.status_code != 200:
    #                 return None, f"Failed to fetch user details: {user_response.status_code} - {user_response.text}"
                

    #             # Handle the response type
    #             user_details = user_response.json()

    #             if isinstance(user_details, list):
    #                 user_details = user_details[0] if user_details else {}  # Assuming the list contains the user details
    #             elif isinstance(user_details, dict):
    #                 user_details = user_details.get("user", {})
                    
    #             # If user details still empty or invalid
    #             if not user_details:
    #                user_details = {}    

            
    #             licenses, error = GsmbOfficerService.get_user_licenses(user_id, token)

    #             if error:
    #                 return None, error

    #             # Combine user details and licenses into one object
    #             owners_with_details_and_licenses.append({
    #                 "id": user_id,
    #                 "owner_name": owner["user"]["name"],
    #                 "user_details": user_details,
    #                 "licenses": licenses
    #             })

    #         return owners_with_details_and_licenses, None

    #    except Exception as e:
    #     return None, f"Server error: {str(e)}"

    # @staticmethod
    # def get_user_licenses(user_id, token):
    #    try:
    #     # Get API Key from the token
    #     api_key = JWTUtils.get_api_key_from_token(token)
    #     if not api_key:
    #         return None, "Invalid or missing API key in the token"

    #     REDMINE_URL = os.getenv("REDMINE_URL")
    #     if not REDMINE_URL:
    #         return None, "Environment variable 'REDMINE_URL' is not set"

    #     headers = {
    #         "X-Redmine-API-Key": api_key,
    #         "Content-Type": "application/json"
    #     }

    #     # Construct URL to get issues for a specific user
    #     url = f"{REDMINE_URL}/projects/GSMB/issues.json?assigned_to_id={user_id}"
    #     response = requests.get(url, headers=headers)
        


    #     if response.status_code != 200:
    #         return None, f"Failed to fetch licenses: {response.status_code} - {response.text}"

    #     issues = response.json().get("issues", [])

    #     if not issues:
    #         return [], None  # Return an empty list if no issues are found

    #     # Filter out issues that are licenses (based on tracker type or custom fields)
    #     licenses = [
    #         issue for issue in issues
    #         if issue.get('tracker', {}).get('name') == 'ML'
    #     ]
    

    #     # After filtering, extract the custom fields and other necessary info for licenses
    #     licenses_data = []
    #     for issue in licenses:
    #         license_number = None
    #         location = None
    #         capacity = None
    #         issue_date = issue.get('start_date')
    #         expiry_date = issue.get('due_date')

    #         # Loop through the custom fields to extract License Number, Location, and Capacity
    #         for field in issue.get('custom_fields', []):
    #           if field.get('name') == 'License Number':
    #             license_number = field.get('value')
    #           elif field.get('name') == 'Location':
    #             location = field.get('value')
    #           elif field.get('name') == 'Capacity':
    #             capacity = field.get('value')


    #         # Add the processed data to licenses_data
    #     licenses_data.append({
    #        'licenseNumber': license_number,
    #        'location': location,
    #        'capacity': capacity,
    #        'issueDate': issue_date,
    #        'expiryDate': expiry_date
    #     })
        

    #     return licenses_data, None
    #    except Exception as e:
    #     return None, f"Server error: {str(e)}"

 
    
    
    
    
    
    
    
       