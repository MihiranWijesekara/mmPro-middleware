import os
from dotenv import load_dotenv
import requests
from utils.MLOUtils import MLOUtils
from utils.jwt_utils import JWTUtils
from utils.limit_utils import LimitUtils
from werkzeug.utils import secure_filename 


load_dotenv()

class MiningEnginerService:

    ORS_API_KEY = os.getenv("ORS_API_KEY")
    
    @staticmethod
    def update_miningOwner_appointment(token,issue_id,update_data):
        try:
            REDMINE_URL = os.getenv("REDMINE_URL")
            API_KEY = JWTUtils.get_api_key_from_token(token)

            if not REDMINE_URL or not API_KEY:
                return None, "Redmine URL or API Key is missing"
            
            payload = {
            "issue": {
                "status_id": update_data.get("status_id", 31),  # Default status ID
                #"description": appointment_data.get("description", ""),
                "due_date": update_data.get("due_date" ), 
                }
            }

            headers = {
            "Content-Type": "application/json",
            "X-Redmine-API-Key": API_KEY
            }

            response = requests.put(
            f"{REDMINE_URL}/issues/{issue_id}.json",
            json=payload,
            headers=headers
            )

            if response.status_code == 201:
                return response.json(), None
            else:
                error_msg = f"Failed to create appointment. Status: {response.status_code}"
                try:
                    error_data = response.json()
                    error_msg += f", Error: {error_data.get('errors', 'Unknown error')}"
                except:
                    error_msg += f", Response: {response.text}"
                return None, error_msg

        except requests.exceptions.RequestException as e:
            return None, f"Request failed: {str(e)}"
        except Exception as e:
            return None, f"Unexpected error: {str(e)}"
        
     
    @staticmethod
    def get_me_pending_licenses(token):
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
                "status_id": 26 
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
                error_msg = f"Redmine API error: {response.status_code}"
                if response.text:
                    error_msg += f" - {response.text[:200]}"  # Truncate long error messages
                return None, error_msg

            data = response.json()
            issues = data.get("issues", [])

            processed_issues = []
            for issue in issues:
                # Process custom fields using IDs
                custom_fields = {field['id']: field['value']
                                for field in issue.get('custom_fields', [])
                                if field.get('value') and str(field.get('value')).strip()}

                attachment_urls = MiningEnginerService.get_attachment_urls(API_KEY, REDMINE_URL, issue.get("custom_fields", []))

                processed_issues.append({
                    "id": issue.get("id"),
                    "subject": issue.get("subject"),
                    "status": issue.get("status", {}).get("name"),
                    "assigned_to": issue.get("assigned_to", {}).get("name"),
                    "exploration_license_no": custom_fields.get(19),  # ID for "Exploration Licence No"
                    "Land_Name": custom_fields.get(28),  # ID for "Land Name(Licence Details)"
                    "Land_owner_name": custom_fields.get(29),  # ID for "Land owner name"
                    "Name_of_village": custom_fields.get(30),  # ID for "Name of village"
                    "Grama_Niladhari": custom_fields.get(31),  # ID for "Grama Niladhari Division"
                    "Divisional_Secretary_Division": custom_fields.get(32),  # ID for "Divisional Secretary Division"
                    "administrative_district": custom_fields.get(33),  # ID for "Administrative District"
                    "Capacity": custom_fields.get(34),  # ID for "Capacity"
                    "Mobile_Numbe": custom_fields.get(66),  # ID for "Mobile Number"
                    "Google_location": custom_fields.get(92),  # ID for "Google location"
                    "Detailed_Plan": attachment_urls.get("Detailed Mine Restoration Plan") or custom_fields.get(72),  # ID for "Detailed Mine Restoration Plan"
                    "Payment_Receipt": attachment_urls.get("Payment Receipt") or custom_fields.get(80),  # ID for "Payment Receipt"
                    "Deed_Plan": attachment_urls.get("Deed and Survey Plan") or custom_fields.get(90),  # ID for "Deed and Survey Plan"
                })

            return processed_issues, None

        except Exception as e:
            return None, f"Server error: {str(e)}"
    
    @staticmethod
    def get_attachment_urls(api_key, redmine_url, custom_fields):
        try:
            # Define the mapping of custom field names to their attachment IDs
            file_fields = {
                "Detailed Mine Restoration Plan": None,
                "Deed and Survey Plan": None,
                "Payment Receipt": None     
            }

            # Extract attachment IDs from custom fields
            for field in custom_fields:
                field_name = field.get("name")
                attachment_id = field.get("value")

                if field_name in file_fields and attachment_id.isdigit():
                    file_fields[field_name] = attachment_id

            # Fetch URLs for valid attachment IDs
            file_urls = {}
            for field_name, attachment_id in file_fields.items():
                if attachment_id:
                    attachment_url = f"{redmine_url}/attachments/{attachment_id}.json"
                    response = requests.get(
                        attachment_url,
                        headers={"X-Redmine-API-Key": api_key, "Content-Type": "application/json"}
                    )

                    if response.status_code == 200:
                        attachment_data = response.json().get("attachment", {})
                        file_urls[field_name] = attachment_data.get("content_url", "")

            return file_urls

        except Exception as e:
            return {}
        

    @staticmethod
    def miningEngineer_approve(token,issue_id,update_data,attachments=None):   
        try:
            REDMINE_URL = os.getenv("REDMINE_URL")
            API_KEY = JWTUtils.get_api_key_from_token(token)

            if not REDMINE_URL or not API_KEY:
                return None, "Redmine URL or API Key is missing"
            
            payload = {
            "issue": {
                "status_id": update_data.get("status_id", 32),    
                "start_date": update_data.get("start_date", ""),  # Optional start date
                "due_date": update_data.get("due_date", ""),  # Optional due date
                "custom_fields": [
                    {
                        "id": 34,  
                        "value": update_data.get("Capacity", "")
                    },
                    {
                        "id": 99,  
                        "value": update_data.get("month_capacity", "")
                    },
                    {
                        "id": 96,  
                        "value": update_data.get("me_comment", "")
                    },
                    *update_data.get("custom_fields", []) 
                ]              

                }
            }

            headers = {
            "Content-Type": "application/json",
            "X-Redmine-API-Key": API_KEY
            }

            response = requests.put(
            f"{REDMINE_URL}/issues/{issue_id}.json",
            json=payload,
            headers=headers
            )

            if response.status_code == 201:
                return response.json(), None
            
            issue_id = response.json()["issue"]["id"]
            
            if attachments:
                for custom_field_id, file_obj  in attachments.items():
                    try:
                        # Prepare file upload headers - same as in your working upload_file_to_redmine
                        upload_headers = {
                            "X-Redmine-API-Key": API_KEY, 
                           "Content-Type": "application/octet-stream"
                        }

                        filename = secure_filename(file_obj.filename)
                        upload_url = f"{REDMINE_URL}/uploads.json?filename={filename}"
                    
                        upload_response = requests.post(
                        upload_url,
                        headers=upload_headers,
                        data=file_obj.stream.read()
                        )
                 
                        if upload_response.status_code != 201:
                            print(f"Failed to upload file for field {custom_field_id}: {upload_response.text}")
                            continue
                
                        upload_token = upload_response.json().get("upload", {}).get("token")
                        if not upload_token:
                            print(f"No upload token received for field {custom_field_id}")
                            continue
                
                        # Update the issue with the attachment token
                        update_payload = {
                            "issue": {
                                "custom_fields": [
                                    {
                                        "id": int(custom_field_id),
                                        "value": upload_token
                                    }
                                ]
                            }
                        }
                
                        update_response = requests.put(
                            f"{REDMINE_URL}/issues/{issue_id}.json",
                            json=update_payload,
                            headers=headers
                        )
                
                        if update_response.status_code != 200:
                            print(f"Failed to update field {custom_field_id}: {update_response.text}")


                        if attachments:
                            for custom_field_id, file_obj  in attachments.items():
                                try:
                        
                                    upload_headers = {
                                        "X-Redmine-API-Key": API_KEY, 
                                        "Content-Type": "application/octet-stream"
                                    }

                                    filename = secure_filename(file_obj.filename)
                                    upload_url = f"{REDMINE_URL}/uploads.json?filename={filename}"
                    
                                    upload_response = requests.post(
                                    upload_url,
                                    headers=upload_headers,
                                    data=file_obj.stream.read()
                                    )
                 
                                    if upload_response.status_code != 201:
                                        print(f"Failed to upload file for field {custom_field_id}: {upload_response.text}")
                                        continue
                
                                    upload_token = upload_response.json().get("upload", {}).get("token")
                                    if not upload_token:
                                        print(f"No upload token received for field {custom_field_id}")
                                        continue
                
                                    # Update the issue with the attachment token
                                    update_payload = {
                                        "issue": {
                                            "custom_fields": [
                                                {
                                                "id": int(custom_field_id),
                                                "value": upload_token
                                                }
                                            ]
                                        }
                                   }
                
                                    update_response = requests.put(
                                        f"{REDMINE_URL}/issues/{issue_id}.json",
                                        json=update_payload,
                                        headers=headers
                                    )
                
                                    if update_response.status_code != 200:
                                        print(f"Failed to update field {custom_field_id}: {update_response.text}")
            
                                except Exception as e:
                                    print(f"Error processing attachment for field {custom_field_id}: {str(e)}")
    
                                    return response.json(), None    
            

                        return response.json(), None
                
                    except requests.exceptions.RequestException as e:
                        return None, f"Request failed: {str(e)}"
        except Exception as e:
            return None, f"Unexpected error: {str(e)}"
  


