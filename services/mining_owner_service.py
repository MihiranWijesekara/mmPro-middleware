from typing import Dict, List, Optional, Tuple
import requests
import os
from dotenv import load_dotenv
import json
from datetime import date, timedelta , datetime 
from services.general_public_service import GeneralPublicService
from utils.jwt_utils import JWTUtils
from utils.MLOUtils import MLOUtils
from flask import request
from utils.limit_utils import LimitUtils
from werkzeug.utils import secure_filename

load_dotenv()

class MLOwnerService:

    ORS_API_KEY = os.getenv("ORS_API_KEY")
    

    @staticmethod
    def mining_licenses(token):
        try:
            print("Starting mining_licenses method...")
            REDMINE_URL = os.getenv("REDMINE_URL")
            API_KEY = JWTUtils.get_api_key_from_token(token)

            if not REDMINE_URL or not API_KEY:
                print("Redmine URL or API Key is missing")
                return None, "Redmine URL or API Key is missing"

            # Step 1: Extract user_id from the token
            user_id, error = MLOUtils.get_user_info_from_token(token)
            if not user_id:
                print(f"Error extracting user_id: {error}")
                return None, error

            print(f"User ID from token: {user_id}")

            # Step 2: Define query parameters for project_id=1 and tracker_id=4 (ML)
            params = {
                "project_id": 1,
                "tracker_id": 4,  # ML tracker ID
                "status_id": 7 
            }

            headers = {
                "Content-Type": "application/json",
                "X-Redmine-API-Key": API_KEY
            }

            limit = LimitUtils.get_limit()
            print(f"Fetching issues with limit: {limit}")
            response = requests.get(
                f"{REDMINE_URL}/projects/mmpro-gsmb/issues.json?offset=0&limit={limit}",
                params=params,
                headers=headers
            )

            # Check if the request was successful
            if response.status_code != 200:
                print(f"Failed to fetch issues: {response.status_code} - {response.text}")
                return None, f"Failed to fetch issues: {response.status_code} - {response.text}"

            issues = response.json().get("issues", [])
            print(f"Fetched {len(issues)} issues")

            # Step 3: Filter the issues based on the logged-in user's user_id
            filtered_issues = [
                issue for issue in issues if MLOUtils.issue_belongs_to_user(issue, user_id)
            ]
            print(f"Filtered {len(filtered_issues)} issues for user {user_id}")
 
            # Step 4: Extract and format the required fields
            relevant_issues = []
            for issue in filtered_issues:
                # Extract custom fields
                custom_fields = issue.get("custom_fields", [])
                custom_fields_dict = {field["name"]: field["value"] for field in custom_fields}

                # Get required fields
                license_number = custom_fields_dict.get("Mining License Number", "N/A")  # License number is in the "subject" field
                owner_name = custom_fields_dict.get("Name of Applicant OR Company", "N/A")
                location = custom_fields_dict.get("Name of village ", "N/A")
                start_date = issue.get("start_date", "N/A")
                due_date = issue.get("due_date", "N/A")
                remaining_cubes = int(custom_fields_dict.get("Remaining", 0))
                roylaty = int(custom_fields_dict.get("Royalty", 0))

                # Determine status
                current_date = datetime.now().date()
                due_date_obj = datetime.strptime(due_date, "%Y-%m-%d").date() if due_date != "N/A" else None

                if due_date_obj and (current_date > due_date_obj or remaining_cubes <= 0):
                    status = "Expired"
                else:
                    status = "Active"

                # Append formatted issue data
                relevant_issues.append({
                    "License Number": license_number,
                    "Owner Name": owner_name,
                    "Location": location,
                    "Start Date": start_date,
                    "Due Date": due_date,
                    "Status": status,
                    "Royalty": roylaty
                })

            print("Returning relevant issues")
            return relevant_issues, None  # Returning filtered issues and no error

        except Exception as e:
            print(f"Exception in mining_licenses: {str(e)}")
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

            # Step 2: Define query parameters for project_id=1 and tracker_id=4 (ML)
            params = {
                "project_id": 1,
                "tracker_id": 4,  # ML tracker ID
                "status_id": 7 
            }

            headers = {
                "X-Redmine-API-Key": API_KEY
            }

            # Make the Redmine request
            limit = LimitUtils.get_limit()
            response = requests.get(
                f"{REDMINE_URL}/projects/mmpro-gsmb/issues.json?offset=0&limit={limit}",
                params=params,
                headers=headers
            )

            # Check if the request was successful
            if response.status_code != 200:
                return None, f"Failed to fetch issues: {response.status_code} - {response.text}"

            issues = response.json().get("issues", [])

            # Step 3: Filter the issues based on the logged-in user's user_id
            filtered_issues = [
                issue for issue in issues if MLOUtils.issue_belongs_to_user(issue, user_id)
            ]

            filtered_issues_sorted = sorted(
            filtered_issues,
            key=lambda x: (
                datetime.strptime(x.get("updated_on"), "%Y-%m-%dT%H:%M:%SZ") if x.get("updated_on") else datetime.min,
                datetime.strptime(x.get("created_on"), "%Y-%m-%dT%H:%M:%SZ") if x.get("created_on") else datetime.min
            ),
            reverse=True
            )
            
            relevant_issues = []
            for issue in filtered_issues_sorted:
                # Extract custom fields
                custom_fields = issue.get("custom_fields", [])
                custom_fields_dict = {field["name"]: field["value"] for field in custom_fields}

                # Get required fields
                license_number = custom_fields_dict.get("Mining License Number", "N/A")  

                license_number = custom_fields_dict.get("Mining License Number", "N/A")  
                divisional_secretary = custom_fields_dict.get("Divisional Secretary Division", "N/A")
                owner_name = issue.get("Name of Applicant OR Company", "N/A")
                location = custom_fields_dict.get("Name of village ", "N/A")
                start_date = issue.get("start_date", "N/A")
                due_date = issue.get("due_date", "N/A")
                remaining_cubes = int(custom_fields_dict.get("Remaining", 0))
                royalty = custom_fields_dict.get("Royalty", "N/A")
                

                # Determine status
                current_date = datetime.now().date()
                due_date_obj = datetime.strptime(due_date, "%Y-%m-%d").date() if due_date != "N/A" else None

                if due_date_obj and (current_date > due_date_obj or remaining_cubes <= 0):
                    status = "Expired"
                else:
                    status = "Active"

                # Append formatted issue data
                relevant_issues.append({
                    "License Number": license_number,
                    "Divisional Secretary Division": divisional_secretary,
                    "Owner Name": owner_name,
                    "Location": location,
                    "Start Date": start_date,
                    "Due Date": due_date,
                    "Remaining Cubes": remaining_cubes,
                    "Status": status,
                    "Royalty": royalty
                })

            # Return the relevant issue data
            return relevant_issues, None  # Returning filtered issues and no error

        except Exception as e:
            return None, f"Server error: {str(e)}"

    @staticmethod
    def create_tpl(data, token):
        try:
            # Get the Redmine URL from environment variables
            REDMINE_URL = os.getenv("REDMINE_URL")
            if not REDMINE_URL:
                return None, "Redmine URL is not configured"

            print("Redmine URL:", REDMINE_URL)

            # First check if lorry already has an active TPL license
            # lorry_number = data.get("lorry_number")
            # if lorry_number:
            #     is_valid, error = GeneralPublicService.is_lorry_number_valid(lorry_number)
            # if error:
            #     return None, f"Error checking lorry license status: {error}"
            # if is_valid:
            #     return None, "This lorry already has an active Transport License"

            # Get the API key from the token
            API_KEY = JWTUtils.get_api_key_from_token(token)
            if not API_KEY:
                return None, "Invalid or missing API key"

            # print("API Key:", API_KEY)

            # Fetch the current mining license issue to get Used and Remaining values
            mining_license_number = data.get("mining_license_number")
            if not mining_license_number:
                return None, "Mining license number is required"

            try:
                # Extract the issue ID from the license number
                mining_issue_id = mining_license_number.strip().split('/')[-1]
                mining_issue_id = int(mining_issue_id)  # Make sure it's an integer
            except (IndexError, ValueError):
                return None, "Invalid mining license number format"

            # Define the Redmine API endpoint to fetch the mining license issue directly
            mining_issue_url = f"{REDMINE_URL}/issues/{mining_issue_id}.json"
            headers = {
                "Content-Type": "application/json",
                "X-Redmine-API-Key": API_KEY
            }

            # Fetch the mining license issue
            mining_issue_response = requests.get(mining_issue_url, headers=headers)
            if mining_issue_response.status_code != 200:
                return None, f"Failed to fetch mining license issue: {mining_issue_response.status_code} - {mining_issue_response.text}"

            # Log the Redmine API response for debugging
            mining_issue_data = mining_issue_response.json()
            print("Mining Issue Response:", mining_issue_data)

            # Get the issue details
            mining_issue = mining_issue_data.get("issue")
            if not mining_issue:
                return None, "Mining license issue not found"

            # Extract current Used, Remaining, Royalty values
            custom_fields = mining_issue.get("custom_fields", [])
            used_field = next((field for field in custom_fields if field.get("name") == "Used"), None)
            remaining_field = next((field for field in custom_fields if field.get("name") == "Remaining"), None)
            royalty_field = next((field for field in custom_fields if field.get("name") == "Royalty"), None)

            if not used_field or not remaining_field or not royalty_field:
                return None, "Required fields (Used, Remaining, or Royalty) not found in the mining license issue"
            
            current_used = int(used_field.get("value", 0))
            current_remaining = int(remaining_field.get("value", 0))
            current_royalty = int(royalty_field.get("value", 0))

            cubes = int(data.get("cubes", 0))

            # Calculate TPL cost (500 per cube)
            tpl_cost = cubes * 500

            if current_royalty < tpl_cost:
                return None, f"Insufficient royalty balance. Required: {tpl_cost}, Available: {current_royalty}"
            # Update Used and Remaining values
            new_used = current_used + cubes
            new_remaining = current_remaining - cubes
            new_royalty = current_royalty - tpl_cost

            if new_remaining < 0:
                return None, "Insufficient remaining cubes"

            # Prepare payload to update the mining license issue
            update_payload = {
                "issue": {
                    "custom_fields": [
                        {"id": used_field.get("id"), "value": str(new_used)},
                        {"id": remaining_field.get("id"), "value": str(new_remaining)},
                        {"id": royalty_field.get("id"), "value": str(new_royalty)}
                    ]
                }
            }
            # Log the update payload for debugging
            print("Update Payload:", update_payload)


            # Send a PUT request to update the mining license issue
            update_url = f"{REDMINE_URL}/issues/{mining_issue_id}.json"
            update_response = requests.put(update_url, json=update_payload, headers=headers)
            print("Mining License id url:", update_url)
             # Log the Redmine API response for debugging
            print("Update Response Status Code:", update_response.status_code)
            # print("Update Response Body:", update_response.json())  

            if update_response.status_code != 204:
                return None, "Failed to update mining license issue"

            # Define the Redmine API endpoint for creating the TPL issue
            REDMINE_API_URL = f"{REDMINE_URL}/issues.json"

                    # Extract route_01 and destination for time calculation
            route_01 = data.get("route_01", "")
            destination = data.get("destination", "")

            # Calculate estimated time between route_01 and destination
            time_result = MLOwnerService.calculate_time(route_01, destination)
            print(time_result)
            if not time_result.get("success"):
                return None, time_result.get("error")

            time_hours = time_result.get("time_hours", 0)

            print("the token is ", token)
            result = JWTUtils.decode_jwt_and_get_user_id(token)

            user_id = result['user_id']
            
            print("assinging  id : " , user_id)
            # Prepare the payload for the TPL request
            payload = {
                "issue": {
                    "project_id": 1,  # Replace with actual project ID
                    "tracker_id": 5,  # TPL tracker ID
                    "status_id": 8,   # Active status
                    "priority_id": 2,
                    "subject": "TPL",
                    "start_date": data.get("start_date", date.today().isoformat()),
                    "assigned_to_id": user_id,
                   # "due_date": (datetime.now() + timedelta(hours=time_hours)).strftime("%Y-%m-%d"),
                    "estimated_hours" :time_hours,
                    "custom_fields": [
                        {"id": 53, "name": "Lorry Number", "value": data.get("lorry_number", "")},
                        {"id": 54, "name": "Driver Contact", "value": data.get("driver_contact", "")},
                        {"id": 55, "name": "Route 01", "value": data.get("route_01", "")},
                        {"id": 56, "name": "Route 02", "value": data.get("route_02", "")},
                        {"id": 57, "name": "Route 03", "value": data.get("route_03", "")},
                        {"id": 58, "name": "Cubes", "value": str(cubes)},
                        {"id": 59, "name": "Mining License Number", "value": mining_license_number},
                        {"id": 68, "name": "Destination", "value": data.get("destination", "")}
                    ]
                }
            }

            response = requests.post(REDMINE_API_URL, json=payload, headers=headers)

            print("TPL Issue Creation Response Status Code:", response.status_code)
            print("TPL Issue Creation Response Body:", response.text)  # Debugging line

            # Check if the response is empty before parsing as JSON
            if response.status_code == 201:
                if response.text.strip():  # Ensure there is a response body
                    return response.json(), None
                else:
                    return {"message": "TPL issue created, but Redmine returned an empty response"}, None
            else:
                return None, response.text or "Failed to create TPL issue"


        except Exception as e:
            return None, str(e)
        
    @staticmethod
    def calculate_time(city1, city2):
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
                url = f"https://nominatim.openstreetmap.org/search?q={city_name}&format=json"
                headers = {
                    "User-Agent": "YourAppName/1.0 (your.email@example.com)"  # <-- important for Nominatim usage policy
                }
                response_first = requests.get(url, headers=headers, timeout=1)
                
                if response_first.status_code != 200:
                    raise ValueError(f"Geocoding failed with status code {response_first.status_code}, body: {response_first.text}")

                try:
                    response = response_first.json()
                except ValueError:
                    raise ValueError(f"Invalid JSON response: {response_first.text}")  
                
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
                "Authorization": MLOwnerService.ORS_API_KEY,
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
                "time_hours": int(round(time_hours))
            }
        except Exception as e:
            return {"success": False, "error": str(e)}


   
    def update_issue(issue_id, data):
        try:
            REDMINE_URL = os.getenv("REDMINE_URL")
            API_KEY = os.getenv("REDMINE_ADMIN_API_KEY")

            if not REDMINE_URL or not API_KEY:
                return None, "Redmine URL or API Key is missing"
            headers = {
                "X-Redmine-API-Key": API_KEY,  # Include the token for authorization
                "Content-Type": "application/json"
            }
            update_data = {"issue": data}  # Ensure "issue" is wrapped correctly

            print("------------------------------------------------")
            print("Request Payload:", data)
            print("------------------------------------------------")
            print('\n\n\n\n\n')
            print("data payload", json.dumps(data))
            print('Headers', headers)
            url = f"{REDMINE_URL}/issues/{issue_id}.json"
            print("URL:", url)
            response = requests.put(
                url,
                json = data,  # Ensure correct JSON structure
                headers=headers
            )

            print("Response Status Code:", response.status_code)
            print("Response Headers:", response.headers)

            # Check if response is empty (204 No Content)
            if response.status_code == 204:
                return {"message": "Issue updated successfully, but no content returned"}, None

            # If status is not OK, return the error message
            if response.status_code != 200:
                return None, f"Failed to update issue: {response.status_code} - {response.text}"

            # Attempt to parse the JSON response
            try:
                issue = response.json().get("issue", {})
                return issue, None
            except json.JSONDecodeError:
                return None, "Invalid JSON response from server"

        except Exception as e:
            return None, f"Server error: {str(e)}"

    @staticmethod
    def ml_detail(l_number, token):
        api_key = JWTUtils.get_api_key_from_token(token)
        try:
            REDMINE_URL = os.getenv("REDMINE_URL")

            if not REDMINE_URL or not api_key:
                return None, "Redmine URL or API Key is missing"
            
            
            headers = {
                "X-Redmine-API-Key": api_key,
                "Content-Type": "application/json"
            }
            limit = LimitUtils.get_limit()
            url = f"{REDMINE_URL}/projects/mmpro-gsmb/issues.json?offset=0&limit={limit}"
            # print(f"Requesting: {url}")

            response = requests.get(url, headers=headers)

            if response.status_code != 200:
                return None, f"Failed to fetch issues: {response.status_code} - {response.text}"

            issues = response.json().get("issues", [])

            # Filter issues based on subject matching l_number
            filtered_issues = []
            for issue in issues:
                for field in issue.get("custom_fields", []):
                    if field.get("id") == 101 and field.get("value") == l_number:
                        filtered_issues.append(issue)
                        break

            return filtered_issues[0] if filtered_issues else None, None

        except Exception as e:
            return None, f"Server error: {str(e)}"
        
        
    @staticmethod
    def user_detail(user_id, token):
        api_key = JWTUtils.get_api_key_from_token(token)
        try:
            REDMINE_URL = os.getenv("REDMINE_URL")

            if not REDMINE_URL or not api_key:
                return None, "Redmine URL or API Key is missing"
            headers = {
                "X-Redmine-API-Key": api_key,  # Include the token for authorization
                "Content-Type": "application/json"
            }
            url = f"{REDMINE_URL}/users/{user_id}.json"
            # print("URL:", url)
            response = requests.get(
                url,  # Ensure correct JSON structure
                headers=headers
            )

            if response.status_code != 200:
                return None, f"Failed to fetch issue: {response.status_code} - {response.text}"

            user_detail = response.json().get("user", {})


            return user_detail, None  # Returning filtered issues and no error

        except Exception as e:
            return None, f"Server error: {str(e)}"
     

    @staticmethod
    def view_tpls(token: str, mining_license_number: str) -> Tuple[Optional[List[Dict]], Optional[str]]:
        try:
            print(f"Starting view_tpls for license: {mining_license_number}") # Keep for debugging

            if not mining_license_number or not mining_license_number.strip():
                return None, "Valid mining license number is required"

            mining_license_number = mining_license_number.strip() # Strip once upfront

            # --- Configuration ---
            REDMINE_URL = os.getenv("REDMINE_URL")
            # Assuming JWTUtils has a method like this
            API_KEY = JWTUtils.get_api_key_from_token(token) 

            if not REDMINE_URL or not API_KEY:
                print("Error: Missing REDMINE_URL or API_KEY environment variables or token invalid.") # More specific logging
                return None, "System configuration error - missing Redmine URL or API Key"

            # --- Authentication/User Info (Optional but kept from original) ---
            # Assuming MLOUtils has a method like this
            user_id, error = MLOUtils.get_user_info_from_token(token) 
            if not user_id:
                print(f"Authentication error: {error}") # Log error
                return None, f"Authentication error: {error}"

            # --- Redmine API Call ---
            params = {
                "project_id": 1,          # Matches sample data
                "tracker_id": 5,          # Matches sample data (TPL)
                "cf_59": mining_license_number # Filter by custom field ID 59
                # "status_id": "*" # Optionally add status_id=* to get issues of any status
            }

            headers = {
                "Content-Type": "application/json",
                "X-Redmine-API-Key": API_KEY
            }

            # Assuming LimitUtils has a method like this
            limit = LimitUtils.get_limit() if LimitUtils.get_limit() else 100 # Use a default if needed
            
            api_url = f"{REDMINE_URL}/issues.json" # Simplified URL, project filter is in params
            print(f"Requesting Redmine API: {api_url} with params: {params}") # Debugging

            response = requests.get(
                api_url,
                params={**params, "limit": limit, "offset": 0}, # Combine params
                headers=headers,
                timeout=30 # Add a timeout
            )

            print(f"Redmine API response status: {response.status_code}") # Debugging

            if response.status_code != 200:
                error_msg = f"Redmine API error ({response.status_code}): {response.text}"
                print(error_msg) # Log the error
                return None, error_msg

            # --- Process Results ---
            try:
                response_data = response.json()
                issues = response_data.get("issues", [])
                print(f"Received {len(issues)} issues from Redmine API.") # Debugging
            except ValueError: # Handle cases where response is not valid JSON
                 error_msg = f"Redmine API error: Invalid JSON response. Status: {response.status_code}, Body: {response.text}"
                 print(error_msg)
                 return None, "Failed to parse response from Redmine"


            tpl_list = []
            current_datetime = datetime.now() # Consider timezone if needed

            for issue in issues:
                try:
                    # --- Extract Custom Fields (More Robustly) ---
                    custom_fields_raw = issue.get("custom_fields", [])
                    custom_fields = {
                        field["name"]: field.get("value") # Use .get("value") for safety
                        for field in custom_fields_raw if "name" in field # Ensure field has a name
                    }

                    # --------------------------------------------------------------
                    # REMOVED THE REDUNDANT CHECK HERE:
                    # if custom_fields.get("Mining License Number") != mining_license_number:
                    #    continue
                    # The API filter cf_59=... should handle this already.
                    # If you still face issues, double-check cf_59 is the correct ID
                    # for "Mining issue id" in your Redmine instance.
                    # --------------------------------------------------------------

                    # --- Calculate Status ---
                    created_date_str = issue.get("created_on")
                    estimated_hours_str = issue.get("estimated_hours") # Keep as string initially
                    status = "Undetermined" # Default status

                    if created_date_str and estimated_hours_str is not None: # Check estimated_hours is not None
                        try:
                            created_date = datetime.strptime(created_date_str, "%Y-%m-%dT%H:%M:%SZ")
                            # Make created_date timezone-aware (UTC)
                            # created_date = created_date.replace(tzinfo=timezone.utc) 
                            # If comparing with datetime.now(), make sure both are aware or naive

                            estimated_hours = float(estimated_hours_str) # Convert to float safely here
                            
                            # Calculate expiration datetime
                            expiration_datetime = created_date + timedelta(hours=estimated_hours)

                            # Compare (ensure timezones match if necessary)
                            # For simplicity, assuming naive UTC or local time comparison here
                            if current_datetime < expiration_datetime:
                                status = "Active"
                            else:
                                status = "Expired"

                        except ValueError as e:
                            print(f"Error parsing date/hours for issue {issue.get('id')}: {str(e)}. Date: '{created_date_str}', Hours: '{estimated_hours_str}'")
                            status = "Error Parsing Data" # More specific status
                        except TypeError as e:
                            print(f"Type error during status calculation for issue {issue.get('id')}: {str(e)}. Hours: '{estimated_hours_str}'")
                            status = "Error Calculating Status"

                    # --- Prepare Output Data ---
                    tpl_data = {
                        "tpl_id": issue.get("id"),
                        # Use the value directly from cf_59 if needed, or assume it matches input
                        "license_number": mining_license_number, 
                        # Or fetch from custom_fields if absolutely necessary:
                        # "license_number": custom_fields.get("Mining issue id"), 
                        "subject": issue.get("subject", ""),
                        "status": status,
                        "lorry_number": custom_fields.get("Lorry Number"),
                        "driver_contact": custom_fields.get("Driver Contact"),
                        "destination": custom_fields.get("Destination"),
                        "Route_01": custom_fields.get("Route 01"),
                        "Route_02": custom_fields.get("Route 02"),
                        "Route_03": custom_fields.get("Route 03"),
                        "cubes": custom_fields.get("Cubes"),
                        "Create_Date": created_date_str, # Keep original string format
                        "Estimated Hours": estimated_hours_str, # Keep original value
                    }

                    tpl_list.append(tpl_data)

                except Exception as e:
                    # Log errors processing individual issues but continue with others
                    print(f"Error processing issue {issue.get('id', 'N/A')}: {str(e)}")
                    # Optionally: add a placeholder or skip the issue
                    continue

            print(f"Finished processing. Returning {len(tpl_list)} TPLs.") # Debugging
            return tpl_list, None

        except requests.exceptions.RequestException as e:
            error_msg = f"Network error connecting to Redmine: {str(e)}"
            print(error_msg)
            return None, error_msg
        except Exception as e:
            # Catch unexpected errors during setup or final return
            error_msg = f"Unexpected error in view_tpls: {str(e)}"
            import traceback
            print(error_msg)
            traceback.print_exc() # Print stack trace for debugging
            # Avoid returning the raw exception string to the client for security
            return None, "An unexpected processing error occurred."   


    @staticmethod
    def ml_request(data, token, user_mobile):
        try:
            # Get the Redmine URL from environment variables
            REDMINE_URL = os.getenv("REDMINE_URL")
            if not REDMINE_URL:
                return None, "Redmine URL is not configured"

            print("Redmine URL:", REDMINE_URL)

            # Get the API key from the token
            API_KEY = JWTUtils.get_api_key_from_token(token)
            if not API_KEY:
                return None, "Invalid or missing API key"
            
            headers = {
                "Content-Type": "application/json",
                "X-Redmine-API-Key": API_KEY
            }
    
            # Prepare the payload for the ML request
            payload = {
                "issue": {
                    "project_id": data.get("project_id", 1),
                    "tracker_id": data.get("tracker_id", 4),
                    "status_id": data.get("status_id", 8),
                    "priority_id": data.get("priority_id", 2),
                    "assigned_to_id": data.get("assigned_to"),  # Get from data dictionary
                    "author_id": data.get("author"), 
                    "subject": data.get("subject", "ML Request"),
                    "description": data.get("description", ""),
                    "custom_fields": [
                        {"id": 19, "value": data.get("exploration_nb", "")},
                        {"id": 28, "value": data.get("land_name", "")},  
                        {"id": 29, "value": data.get("land_owner_name", "")},
                        {"id": 30, "value": data.get("village_name", "")},
                        {"id": 31, "value": data.get("grama_niladari", "")},
                        {"id": 32, "value": data.get("divisional_secretary_division", "")},
                        {"id": 33, "value": data.get("administrative_district", "")},   
                        {"id": 92, "value": data.get("google_location", "")}, 
                        {"id": 66, "value": user_mobile},
                        *data.get("custom_fields", [])                              
                    ]
                }
            }

            # First create the issue
            response = requests.post(f"{REDMINE_URL}/issues.json", json=payload, headers=headers)
            
            if response.status_code != 201:
                return None, f"Failed to create issue: {response.text}"
        
            issue_id = response.json()["issue"]["id"]
            
            return response.json(), None

        except requests.exceptions.RequestException as e:
            return None, f"Request failed: {str(e)}"
        except Exception as e:
            return None, f"Unexpected error: {str(e)}"
        
                